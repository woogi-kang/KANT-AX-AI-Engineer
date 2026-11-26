// 기획안(2026-11-26 승인) 기준 시안 v10~v14가 같이 쓰는 내용이에요.
// 로드맵 레포 내용은 v9/snapshot.json(snap.mjs가 만든 것), 강의 내용은 curriculum.json과 챕터 README에서 읽어요. 숫자는 두 레포에 있는 값만 써요.
import fs from "node:fs";
import path from "node:path";
import { i, esc, chapters, byNo, stages as lecStages, extras, cur, C, goals, parts, slides, before, prev, next } from "../lib.mjs";
import { searchKit, DLG_CSS, html, deck, pdf } from "../new/content.mjs";

export { i, esc, chapters, byNo, lecStages, extras, cur, C, goals, parts, slides, before, prev, next, searchKit, DLG_CSS, html, deck, pdf };
export const S = JSON.parse(fs.readFileSync(path.join(import.meta.dirname, "../v9/snapshot.json"), "utf8"));
export const GH = (p) => `https://github.com/woogi-kang/ax-engineer-roadmap/blob/main/${p}`;

/* 사이트 공통 */
export const NAME = "풀스택 AI/AX 엔지니어";
export const MENU = [["roadmap", "로드맵", "roadmap.html"], ["lectures", "강의", "chapter.html"], ["library", "사례와 자료", "cases.html"], ["news", "소식", "home.html#news"]];
export const START = ["시작하기", "home.html#start"];
export const FOOT = "공익 목적으로 만드는 공개 자료예요. 가입이나 결제 없이 누구나 처음부터 끝까지 볼 수 있어요.";
export const LIC = [
  `로드맵 내용: <a href="https://github.com/woogi-kang/ax-engineer-roadmap">ax-engineer-roadmap</a> ${S.version}, MIT License`,
  "강의 내용: © 2026 Taewook Kang (woogi). 개인 학습에 자유롭게 보되, 허락 없이 옮겨 싣거나 고쳐 배포할 수 없어요",
];
export const CONTACT = "woogi@memoriz.net";

/* 짧은 이름 */
export const short = (t) => t.replace(/\s*\(.*\)$/, "");
export const stageShort = (t) => t.replace(/ 익히기| 이해하기| 넓히기| 만들기/, "");
export const firstSentence = (s) => s.split(/(?<=다\.)\s/)[0];

/* 로드맵 주제와 강의 챕터 잇기(초안). 실제로는 강의 레포 roadmap-links.json 하나로 둬요 */
export const AREA_LINKS = {
  "software-and-api": ["01", "02", "12", "19", "28", "31", "36", "44"],
  "llm-foundations": ["12", "13", "15"],
  "agent-systems": ["19", "21", "24"],
  "tools-and-mcp": ["11", "19", "44"],
  "evaluation-and-testing": ["39", "45", "46"],
  "production-operations": ["29", "30", "31", "35"],
  "security-and-privacy": ["33", "37", "43", "44"],
};
export const STAGE_LINKS = { 1: [], 2: [...new Set(Object.values(AREA_LINKS).flat())], 3: ["32", "45", "46"], 4: ["09", "10", "44"], 5: ["45"] };
export const SOON = { "llm-foundations": "LLM 호출, 토큰과 비용", "agent-systems": "에이전트 루프, 중단 조건", "tools-and-mcp": "도구 정의, MCP", "evaluation-and-testing": "평가 세트 만들기" };
export const usedBy = {};
for (const [a, nos] of Object.entries(AREA_LINKS)) for (const n of nos) (usedBy[n] ??= []).push(S.stages[1].areas.find((x) => x.id === a).t);
for (const st of [3, 4, 5]) for (const n of STAGE_LINKS[st]) (usedBy[n] ??= []).push(`${st}단계 ${stageShort(S.stages[st - 1].title)}`);

/* 단계마다 주제 목록 */
export const stageTopics = (s) => s.docs?.map((d) => d.t) ?? s.areas?.map((a) => a.t) ?? s.steps?.map((x) => x.t) ?? s.projects?.map((p) => p.t) ?? S.cases.slice(0, 5).map((c) => c.t);
export const stageCount = (s) => (s.docs ? `문서 ${s.docs.length}개` : s.areas ? `기술 ${s.areas.length}영역` : s.steps ? `업무 전환 ${s.steps.length}단계` : s.projects ? `프로젝트 ${s.projects.length}개` : `업무 사례 ${S.cases.length}개`);

/* 주제 화면 예시: 2단계 소프트웨어와 API. 본문은 로드맵 문서를 그대로 그려요 */
const mdi = (s) => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/\[([^\]]+)\]\(([^)]+)\)/g, (m, t, h) => `<a href="${h.startsWith("http") ? h : GH("technical-foundations/" + h)}">${t}</a>`);
export const render = (src) => {
  const L = src.split("\n"); let o = "", k = 0; const ids = [];
  while (k < L.length) {
    const l = L[k];
    if (l.startsWith("```")) { const b = []; k++; while (k < L.length && !L[k].startsWith("```")) b.push(L[k++]); o += `<pre><code>${esc(b.join("\n"))}</code></pre>`; k++; continue; }
    if (/^## /.test(l)) { const t = l.slice(3); const id = "s" + ids.length; ids.push([id, t]); o += `<h2 id="${id}">${esc(t)}</h2>`; k++; continue; }
    if (/^### /.test(l)) { o += `<h3>${esc(l.slice(4))}</h3>`; k++; continue; }
    if (/^\|/.test(l)) { const rows = []; while (k < L.length && /^\|/.test(L[k])) rows.push(L[k++]); const r = rows.filter((x) => !/^\|[\s|:-]+\|$/.test(x)).map((x) => x.slice(1, -1).split("|").map((c) => c.trim()));
      o += `<div class="tw"><table><thead><tr>${r[0].map((c) => `<th>${mdi(c)}</th>`).join("")}</tr></thead><tbody>${r.slice(1).map((x) => `<tr>${x.map((c) => `<td>${mdi(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`; continue; }
    if (/^- /.test(l)) { const b = []; while (k < L.length && /^- /.test(L[k])) b.push(L[k++].slice(2)); o += `<ul>${b.map((x) => `<li>${mdi(x)}</li>`).join("")}</ul>`; continue; }
    if (/^\d+\. /.test(l)) { const b = []; while (k < L.length && /^\d+\. /.test(L[k])) b.push(L[k++].replace(/^\d+\. /, "")); o += `<ol>${b.map((x) => `<li>${mdi(x)}</li>`).join("")}</ol>`; continue; }
    if (l.trim()) { const b = []; while (k < L.length && L[k].trim() && !/^(#|\||- |\d+\. |```)/.test(L[k])) b.push(L[k++]); o += `<p>${mdi(b.join(" "))}</p>`; continue; }
    k++;
  }
  return { o, ids };
};
const tparts = S.topicMd.split(/\n(?=## )/);
const tsec = Object.fromEntries(tparts.slice(1).map((p) => [p.split("\n")[0].slice(3), p]));
const ITEM_LINKS = [["31"], ["33", "34"], [], ["32", "36", "37", "43"], ["37"], [], ["29", "30", "33"], ["28"]];
export const TOPIC = {
  area: S.stages[1].areas[0],
  stage: S.stages[1],
  title: tparts[0].replace(/^# /, "").trim(),
  why: tsec["왜 필요한가"].split("\n").slice(1).join(" ").trim(),
  know: [...tsec["알아야 할 것"].matchAll(/^- (.+)$/gm)].map((m, n) => ({ t: m[1], lec: ITEM_LINKS[n] || [] })),
  body: render(tparts.slice(1).filter((p) => !/^## (알아야 할 것|왜 필요한가)/.test(p)).join("\n")),
  lec: AREA_LINKS["software-and-api"],
  prev: null,
  next: S.stages[1].areas[1],
  src: "technical-foundations/software-and-api.md",
};

/* 강의 챕터 화면 예시: 36 */
export const CH = { c: C, goals, parts, slides, before, prev, next, used: usedBy["36"] || [], deck: deck(C), pdf: pdf(C) };

/* 사례와 자료 */
export const IND = { "public-sector": "공공", "manufacturing": "제조", "financial-services": "금융", "healthcare-social-care": "의료·돌봄", "customer-service": "고객 상담", "collaboration": "협업", "software-engineering": "소프트웨어 개발", "retail-ecommerce": "유통·커머스", "education": "교육", "telecommunications": "통신", "logistics": "물류", "media": "미디어", "legal": "법무", "energy": "에너지", "hr": "인사", "travel-hospitality": "여행·숙박", "research": "연구", marketing: "마케팅", "automotive-service": "자동차 서비스", "people-operations": "인사 운영", "consumer-retail": "소비재·리테일", "legal-life-sciences": "법무·생명과학", "b2b-sales": "B2B 영업", travel: "여행", "software-marketing": "소프트웨어 마케팅", "professional-services": "전문 서비스" };
export const indKo = (k) => IND[k] || k;
export const STAGE_KO = { operation: "운영", "limited-operation": "제한 운영", pilot: "파일럿", "adjusted-operation": "조정 운영", unknown: "알 수 없음" };
export const VERIFY_KO = { "self-reported": "자체 발표", "cross-checked": "교차 확인", none: "검증 없음" };
export const OUT_KO = { STOPPED: "중단", PAUSED: "일시 중단", SANCTIONED: "제재", SCALED_BACK: "축소", UNPROVEN: "미입증", REVERSED: "되돌림" };
export const LIB = [
  ["cases", "업무 사례", S.cases.length, "업무 하나를 원본 시스템, 승인 지점, 실패 대응까지 설계한 문서"],
  ["public", "공개 AX 사례", S.publicCases.n, `국내 ${S.publicCases.kr}개 포함, 주장마다 출처와 확인일`],
  ["failures", "실패·중단 사례", S.failures.n, "바꾸려던 일, 결과, 원인, 다시 하지 않을 점검"],
  ["templates", "실무 템플릿", S.toolkit.reduce((a, t) => a + t.items.length, 0), "업무 발굴부터 재사용까지 바로 복사해 쓰는 양식"],
  ["jobs", "채용 현황", S.hiring.rows.reduce((a, r) => a + r.n, 0), "2026년 10월 국내 AX·AI Agent·FDE 공고"],
];
export const HIRE_TOTAL = S.hiring.rows.reduce((a, r) => a + r.n, 0);
export const AREAS = [...new Set(S.cases.map((c) => c.area))];

/* 소식: 두 레포에서 바뀐 것을 날짜순으로 */
export const NEWS = [
  ["2026-11-24", "강의", "46 데이터 정리하기 (타이타닉 전처리)를 올렸어요"],
  ["2026-11-23", "강의", "모든 슬라이드에 PDF 받기를 더했어요"],
  ["2026-10-28", "로드맵", "공개 실패·중단 사례 16개와 월간 채용 현황을 더했어요"],
  ["2026-10-27", "로드맵", `${S.version}: 업무 사례를 15개로 늘렸어요`],
];

/* 찾기 */
export const kitFor = (topicHref = "topic.html", chHref = "chapter.html") => searchKit([
  ...S.stages.flatMap((s) => stageTopics(s).map((t) => ({ t, s: `로드맵 ${s.no}단계` }))),
  ...chapters.map((c) => ({ t: `${c.no} ${c.title}`, s: `강의 · ${c.track}` })),
  ...S.cases.map((c) => ({ t: c.t, s: "업무 사례" })),
], topicHref);

/* 화면 다섯 가지: 비교 화면에서 같은 이름으로 불러요 */
export const SCREENS = [["home", "홈"], ["roadmap", "로드맵"], ["topic", "로드맵 주제"], ["chapter", "강의 챕터"], ["cases", "사례와 자료"]];
