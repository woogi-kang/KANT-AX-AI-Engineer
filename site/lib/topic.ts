// 로드맵 주제 문서(로드맵 레포의 마크다운)를 주제 화면에 맞게 나눠요.
// 문서 모양이 단계마다 달라서(1 문서, 2 기술 영역, 3 업무 전환 단계, 4 프로젝트) 절 이름으로 골라 써요.
// 글은 레포에 있는 그대로 쓰고, 사이트에서 새 문장이나 숫자를 만들지 않아요.
import { readRm, roadmap, strip, type Topic } from "./roadmap";
import { renderRoadmapMd } from "./markdown";

export type Sec = { title: string; md: string };
export type Card = { t: string; d?: string; id?: string };

/** "## 제목" 단위로 나눈 절(앞에 붙은 "1. " 번호는 그대로) */
export function topicSections(t: Topic): { intro: string; secs: Sec[] } {
  const md = readRm(t.path).replace(/^# .+\n+/m, "");
  const parts = md.split(/\n(?=## )/);
  const intro = parts[0].startsWith("## ") ? "" : parts.shift()!.trim();
  const secs = parts.map((p) => ({ title: p.split("\n")[0].slice(3).trim(), md: p.split("\n").slice(1).join("\n").trim() }));
  return { intro, secs };
}

export const findSec = (secs: Sec[], re: RegExp) => secs.find((s) => re.test(s.title));
/** 절의 맨 앞 목록(- 또는 1.)을 글 배열로 */
export const listOf = (md = "") =>
  md
    .split("\n")
    .filter((l) => /^(- |\d+\. )/.test(l))
    .map((l) => strip(l.replace(/^(- |\d+\. )/, "")).replace(/`([^`]+)`/g, "‘$1’"));
/** 첫 문단 */
export const firstPara = (md = "") => strip(md.split("\n\n").find((p) => p.trim() && !/^(\||```|- |\d+\. )/.test(p.trim())) ?? "").replace(/`([^`]+)`/g, "‘$1’").replace(/\n/g, " ");
/** "### 제목" 단위로 나눈 작은 절 */
export function subSections(md: string): Sec[] {
  return md
    .split(/\n(?=### )/)
    .filter((p) => p.startsWith("### "))
    .map((p) => ({ title: p.split("\n")[0].slice(4).trim(), md: p.split("\n").slice(1).join("\n").trim() }));
}

/* ---------- 흐름 그림 ---------- */
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
type Flow = { steps: string[][]; loop?: string };
function flowHtml(f: Flow) {
  const li = f.steps.map((lines, n) => `<li><span class="fl-n">${n + 1}</span><span class="fl-t">${lines.map((l, k) => (k ? `<small>${esc(l)}</small>` : `<b>${esc(l)}</b>`)).join("")}</span></li>`).join("");
  return `<div class="flowbox"><ol class="flow">${li}</ol>${f.loop ? `<p class="loop">↻ ${esc(f.loop)}</p>` : ""}</div>`;
}
/** 한 줄로 이어지는 mermaid flowchart만 그림으로 바꿔요. 갈래가 있으면 null */
export function parseMermaid(src: string): Flow | null {
  const label: Record<string, string> = {};
  const edges: [string, string, string?][] = [];
  for (const raw of src.split("\n").slice(1)) {
    const line = raw.trim();
    if (!line) continue;
    for (const m of line.matchAll(/(\w+)\["([^"]+)"\]/g)) label[m[1]] = m[2];
    const plain = line.replace(/\["[^"]+"\]/g, "");
    const toks = plain.split(/\s*(-->(?:\|"[^"]*"\|)?|-\.\s*"[^"]*"\s*\.->)\s*/);
    for (let k = 1; k + 1 < toks.length; k += 2) {
      const lbl = /"([^"]*)"/.exec(toks[k])?.[1];
      edges.push([toks[k - 1].trim(), toks[k + 1].trim(), lbl]);
    }
  }
  if (!edges.length) return null;
  const order = [edges[0][0]];
  let loop: string | undefined;
  for (const [a, b, l] of edges) {
    if (order[order.length - 1] !== a) return null;
    if (order.includes(b)) {
      loop = l ?? "";
      continue;
    }
    order.push(b);
  }
  return { steps: order.map((id) => (label[id] ?? id).split("<br/>")), loop };
}
/** "→ "로 시작하는 줄이 이어지는 text 칸 */
export function parseArrowText(src: string): Flow | null {
  const lines = src.split("\n").filter((l) => l.trim());
  if (lines.length < 3 || !lines.slice(1).every((l) => l.startsWith("→ "))) return null;
  return { steps: lines.map((l) => [l.replace(/^→ /, "")]) };
}
/** 마크다운 안의 흐름 코드 칸을 그림 HTML로 바꿔요 */
export function flowsToHtml(md: string) {
  return md.replace(/```(mermaid|text)\n([\s\S]*?)```/g, (all, kind: string, src: string) => {
    const f = kind === "mermaid" ? parseMermaid(src.trim()) : parseArrowText(src.trim());
    return f ? `\n${flowHtml(f)}\n` : all;
  });
}
export function firstFlow(md: string): Flow | null {
  for (const m of md.matchAll(/```(mermaid|text)\n([\s\S]*?)```/g)) {
    const f = m[1] === "mermaid" ? parseMermaid(m[2].trim()) : parseArrowText(m[2].trim());
    if (f) return f;
  }
  return null;
}
export const flowMarkup = flowHtml;

/** 절 하나를 HTML로 */
export const secHtml = (t: Topic, md: string) => renderRoadmapMd(t.path, flowsToHtml(md));

/** 문서 안에서 실무 템플릿으로 가는 링크 */
export function templateLinks(t: Topic) {
  const md = readRm(t.path);
  const r = roadmap();
  const seen = new Set<string>();
  return [...md.matchAll(/\]\((?:\.\.\/)?toolkit\/([a-z0-9-]+)\.md\)/g)]
    .map((m) => r.templates.find((x) => x.slug === m[1]))
    .filter((x): x is NonNullable<typeof x> => !!x && !seen.has(x.slug) && !!seen.add(x.slug));
}

/** 단계 1 문서마다 한눈에 볼 카드. 어느 절에서 무엇을 뽑을지 문서에 맞춰 정해요 */
export function docCards(t: Topic, secs: Sec[]): { title: string; cards: Card[]; cols: 2 | 3 | 4 } | null {
  const slugId = (title: string) => secs.findIndex((s) => s.title === title);
  if (t.slug === "role-model") {
    const s = findSec(secs, /운영 모델/);
    if (!s) return null;
    const rows = s.md.split("\n").filter((l) => /^\|/.test(l) && !/^\|[\s|:-]+\|$/.test(l)).slice(1).map((l) => l.slice(1, -1).split("|").map((c) => strip(c)));
    return { title: s.title.replace(/^\d+\.\s*/, ""), cols: 3, cards: rows.map(([a, b, c, d]) => ({ t: a, d: `${b}. 강점: ${c}. 주의: ${d}.` })) };
  }
  if (t.slug === "ax-engineer-role-review") {
    const s = findSec(secs, /역할 형태/);
    if (!s) return null;
    return { title: s.title, cols: 3, cards: subSections(s.md).map((x) => ({ t: x.title.replace(/^\d+\.\s*/, ""), d: firstPara(x.md) })) };
  }
  if (t.slug === "competency-map") {
    const areas = secs.filter((s) => /^[2-9]\. /.test(s.title));
    return { title: "여덟 영역", cols: 4, cards: areas.map((s, n) => ({ t: `${n + 1}. ${s.title.replace(/^\d+\.\s*/, "")}`, d: listOf(subSections(s.md)[0]?.md).slice(0, 2).join(", "), id: `sec-${slugId(s.title)}` })) };
  }
  if (t.slug === "proficiency-levels") {
    const s = findSec(secs, /네 단계/);
    if (!s) return null;
    return { title: s.title.replace(/^\d+\.\s*/, ""), cols: 4, cards: subSections(s.md).map((x) => ({ t: x.title, d: firstPara(x.md) })) };
  }
  return null;
}
