// 찾기 창이 읽는 목록을 만들어요. 빌드할 때 /search.json 한 파일로 나가요.
import { load } from "./content";
import { roadmap, readRm } from "./roadmap";
import { LIB_NAME, stageShort } from "./site";

export type SearchItem = { t: string; s: string; h: string; k?: string };

const plain = (s = "") => s.replace(/`/g, "").replace(/\*\*/g, "").replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");

/** 용어 사전 표: [용어, 뜻, 물을 질문] */
export function glossary() {
  const md = readRm("start-here/non-developer-glossary.md");
  const first = md.split("\n## ")[0];
  return first
    .split("\n")
    .filter((l) => /^\|/.test(l) && !/^\|[\s|:-]+\|$/.test(l))
    .slice(1)
    .map((l) => l.slice(1, -1).split("|").map((c) => c.trim()))
    .map(([term, mean, ask]) => ({ term, mean, ask, id: "g-" + term.replace(/\s+/g, "-").replace(/[()]/g, "") }));
}

/** 문서 본문에서 찾을 말만 남겨요(표 칸, 목록, 제목). 너무 길면 앞부분만 */
const body = (p: string) =>
  plain(readRm(p))
    .replace(/^#.*$/gm, " ")
    .replace(/[|#>*_-]+/g, " ")
    .replace(/\s+/g, " ")
    .slice(0, 2500);

export function searchItems(): SearchItem[] {
  const { chapters, extras, updates } = load();
  const r = roadmap();
  return [
    ...r.topics.map((t) => ({ t: t.t, s: `로드맵 ${t.stage}단계 · ${stageShort(r.stages[t.stage - 1].title)}`, h: `/roadmap/${t.slug}/`, k: `${t.q ?? ""} ${body(t.path)}` })),
    ...chapters.map((c) => ({ t: `${c.no} ${c.title}`, s: `강의 · ${c.track}`, h: `/chapters/${c.dir}/`, k: plain(`${c.keyword ?? ""} ${c.goal} ${c.commands ?? ""}`) })),
    ...extras.map((e) => ({ t: e.title, s: "꿀팁", h: `/extras/${e.dir}/`, k: plain(e.summary) })),
    ...r.cases.map((c) => ({ t: c.t, s: `${LIB_NAME.cases} · ${c.area}`, h: `/library/cases/${c.id}/`, k: `${c.industry} ${c.scope} ${body(c.path)}` })),
    ...r.publicCases.map((c) => ({ t: `${c.org}: ${c.w}`, s: LIB_NAME.public, h: `/library/public/#${c.id}`, k: c.ind })),
    ...r.failures.map((c) => ({ t: `${c.org}: ${c.change}`, s: LIB_NAME.failures, h: `/library/failures/#${c.id}`, k: c.domain })),
    ...r.templates.map((t) => ({ t: t.t, s: LIB_NAME.templates, h: `/library/templates/${t.slug}/`, k: t.when })),
    ...glossary().map((g) => ({ t: plain(g.term), s: "용어 사전", h: `/glossary/#${g.id}`, k: plain(g.mean) })),
    ...updates.map((u) => ({ t: u.title, s: `소식 · ${u.date}`, h: `/updates/${u.dir}/`, k: u.summary })),
  ];
}
