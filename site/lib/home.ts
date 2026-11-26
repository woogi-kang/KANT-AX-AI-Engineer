// 홈과 사례와 자료 화면이 같이 쓰는 숫자와 시작 타일이에요. 숫자는 두 레포에 있는 값만 세요.
import { roadmap } from "./roadmap";
import type { LibKey } from "./site";

export function libCounts(): Record<LibKey, number> {
  const r = roadmap();
  return { cases: r.cases.length, public: r.publicCases.length, failures: r.failures.length, templates: r.templates.length, jobs: r.hiringTotal };
}

/** 단계 카드 아래 한 줄: "기술 7영역"처럼 */
export function stageCount(no: number) {
  const r = roadmap();
  const n = no === 5 ? r.cases.length : r.stages[no - 1].topics.length;
  return ["", `문서 ${n}개`, `기술 ${n}영역`, `업무 전환 ${n}단계`, `프로젝트 ${n}개`, `업무 사례 ${n}개`][no];
}

/** 홈의 시작 타일. 시작하기 화면(/start/)의 같은 키 자리로 가요 */
export const START = [
  { key: "new", icon: "square-terminal", label: "개발이 처음이에요", href: "/start/#new" },
  { key: "dev", icon: "code-xml", label: "개발 경험이 있어요", href: "/start/#dev" },
  { key: "biz", icon: "briefcase", label: "업무는 잘 알아요", href: "/start/#biz" },
  { key: "words", icon: "book-a", label: "용어부터 낯설어요", href: "/glossary/" },
  { key: "run", icon: "play", label: "코드부터 돌려 볼래요", href: "/start/#run" },
  { key: "class", icon: "presentation", label: "수업을 듣고 있어요", href: "/lectures/" },
] as const;
