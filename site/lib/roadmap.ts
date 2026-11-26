// 빌드할 때 로드맵 레포(woogi-kang/ax-engineer-roadmap, MIT)를 읽어 사이트 데이터로 바꿔요.
// 레포는 scripts/fetch-roadmap.mjs가 site/.roadmap에 받아 두거나, ROADMAP_DIR로 폴더를 적어요.
// 숫자와 글은 레포에 있는 값만 써요. 내용은 사이트에서 고치지 않고 로드맵 레포에서 고쳐요.
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

export const ROADMAP_REPO = "woogi-kang/ax-engineer-roadmap";
export const ROADMAP_URL = `https://github.com/${ROADMAP_REPO}`;
export const RM = process.env.ROADMAP_DIR ? path.resolve(process.env.ROADMAP_DIR) : path.resolve(process.cwd(), ".roadmap");

/** 레포 안 파일의 GitHub 주소 */
export const ghBlob = (p: string) => `${ROADMAP_URL}/blob/main/${p}`;

export function readRm(p: string): string {
  const f = path.join(RM, p);
  if (!fs.existsSync(f)) throw new Error(`로드맵 레포에 없는 파일: ${p}. npm run fetch-roadmap을 먼저 쳐 주세요`);
  return fs.readFileSync(f, "utf8");
}
export const readRmJson = <T = unknown>(p: string): T => JSON.parse(readRm(p)) as T;
export const existsRm = (p: string) => fs.existsSync(path.join(RM, p));

/* ---------- 작은 마크다운 도우미 ---------- */
type Link = { t: string; href?: string };
const linkOf = (s: string): Link => {
  const m = /\[([^\]]+)\]\(([^)]+)\)/.exec(s);
  return m ? { t: m[1], href: m[2] } : { t: s.trim() };
};
/** 굵게와 링크 표시를 지운 글 */
export const strip = (s: string) => s.replace(/\*\*/g, "").replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").trim();
/** 마크다운 표의 본문 줄(머리줄 뺀)을 칸 배열로 */
const table = (block: string) =>
  block
    .split("\n")
    .filter((l) => /^\|/.test(l) && !/^\|[\s|:-]+\|$/.test(l))
    .slice(1)
    .map((l) => l.slice(1, -1).split(" | ").map((c) => c.trim().replace(/^\|\s*/, "")));
const between = (s: string, a: string, b?: string) => {
  const i = s.indexOf(a);
  if (i < 0) return "";
  const j = b ? s.indexOf(b, i + a.length) : -1;
  return s.slice(i + a.length, j < 0 ? undefined : j);
};
/** "## 제목" 단위로 나눈 절 */
export function sections(md: string): { title: string; body: string }[] {
  return md
    .split(/\n(?=## )/)
    .slice(1)
    .map((p) => ({ title: p.split("\n")[0].slice(3).trim(), body: p.split("\n").slice(1).join("\n").trim() }));
}
export const titleOf = (md: string) => (/^# (.+)$/m.exec(md)?.[1] ?? "").trim();

/* ---------- 타입 ---------- */
export type TopicKind = "doc" | "area" | "step" | "project";
export type Topic = {
  /** 사이트 주소 /roadmap/<slug>/ */
  slug: string;
  stage: number;
  /** 단계 안 순서(1부터) */
  n: number;
  kind: TopicKind;
  /** 로드맵 README에 적힌 이름 */
  t: string;
  /** 레포 안 경로 */
  path: string;
  /** 한 줄 설명(단계 1 문서), 질문(단계 2 영역), 결과물(단계 4) */
  q?: string;
  need?: string;
};
export type Stage = {
  no: number;
  title: string;
  lede: string;
  checks: string[];
  topics: Topic[];
};
export type RoadmapCase = {
  id: string;
  area: string;
  industry: string;
  t: string;
  path: string;
  diff: number;
  risk: string;
  scope: string;
  p: string;
  ev: string;
  /** 재현 가능한 실행 예제가 있는지 */
  runnable: boolean;
};
export type PublicCase = { id: string; org: string; w: string; ind: string; region: string; stage: string; verify: string };
export type FailureCase = { id: string; org: string; domain: string; change: string; outcome: string; causes: string[]; check: string };
export type Template = { slug: string; t: string; path: string; when: string };
export type HiringRow = { type: string; n: number; open: number };

let cache: ReturnType<typeof build> | null = null;
export function roadmap() {
  return (cache ??= build());
}

function build() {
  const readme = readRm("README.md");
  const version = /최신 릴리스: `([^`]+)`/.exec(readme)?.[1] ?? "";
  let commit = "";
  let date = "";
  try {
    [commit, date] = execFileSync("git", ["log", "-1", "--format=%h %cs"], { cwd: RM, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] })
      .trim()
      .split(" ");
  } catch {}

  /* 단계 다섯 */
  const blocks = readme.split(/\n### (\d)단계\. /).slice(1);
  const stages: Stage[] = [];
  for (let k = 0; k < blocks.length; k += 2) {
    const body = blocks[k + 1].split("\n## ")[0];
    const [title, ...rest] = body.split("\n");
    const text = rest.join("\n");
    const no = +blocks[k];
    const topics: Topic[] = [];
    const add = (kind: TopicKind, l: Link, extra: Partial<Topic> = {}) => {
      if (!l.href) return;
      topics.push({ slug: path.posix.basename(l.href, ".md"), stage: no, n: topics.length + 1, kind, t: l.t, path: l.href, ...extra });
    };
    if (no === 1) for (const [a, b] of table(text.split("<!--")[0])) add("doc", linkOf(a), { q: strip(b) });
    if (no === 2) for (const [a, b] of table(text)) add("area", linkOf(a), { q: strip(b) });
    if (no === 3) for (const m of text.matchAll(/^\d+\. \[([^\]]+)\]\(([^)]+)\)/gm)) add("step", { t: m[1], href: m[2] });
    if (no === 4) for (const [a, b, c] of table(text)) add("project", linkOf(a), { q: strip(b), need: strip(c) });
    stages.push({
      no,
      title: title.trim(),
      lede: strip(text.trim().split("\n\n")[0]),
      checks: [...text.matchAll(/^- \[ \] (.+)$/gm)].map((m) => strip(m[1])),
      topics,
    });
  }
  const topics = stages.flatMap((s) => s.topics);
  const slugs = new Set<string>();
  for (const t of topics) {
    if (slugs.has(t.slug)) throw new Error(`로드맵 주제 주소가 겹쳐요: ${t.slug}`);
    slugs.add(t.slug);
  }

  /* 정의, 하는 일, 시작점 */
  const defn = strip(readme.split("\n# AX Engineer Roadmap")[1]?.split("\n\n")[2] ?? "");
  const role = table(between(readme, "## AX 엔지니어는 어떤 일을 하나요?", "[역할 모델")).map(([does, not]) => ({ does: strip(does), not: strip(not) }));
  const start = table(between(readme, "## 나에게 맞는 시작점", "직함보다")).map(([who, go, first]) => ({ who, go: strip(go), goLinks: [...go.matchAll(/\[([^\]]+)\]\(([^)]+)\)/g)].map((m) => ({ t: m[1], href: m[2] })), first: strip(first) }));
  const faq = sections(between(readme, "## 자주 묻는 질문", "\n## 자료 원칙").replace(/^### /gm, "## ")).map((s) => ({ q: s.title, a: s.body }));

  /* 업무 사례 */
  const cs = readRm("case-studies/README.md");
  const cases: RoadmapCase[] = table(between(cs, "## 업무별 사례 목록", "사례명과")).map(([field, c, lv, , scope, p, ev]) => {
    const [area, industry] = field.split(" · ");
    const [diff, risk] = lv.split(" · ");
    const l = linkOf(c);
    const href = l.href ?? "";
    return { id: href.split("/")[0], area, industry, t: l.t, path: `case-studies/${href}`, diff: +diff, risk, scope, p, ev: strip(ev), runnable: /재현 가능/.test(ev) };
  });

  /* 공개 사례, 실패·중단 사례 */
  type Pub = { id: string; organization: string; workflow: { ko: string }; industry: string; region: string; deployment_stage: string; outcome_verification: string };
  type Fail = { id: string; organization: string; domain: { ko: string }; attempted_change: { ko: string }; outcome: string; failure_causes: string[]; capstone_check: { ko: string } };
  const pubRaw = readRmJson<{ cases: Pub[] }>("research/public-ax-cases.json").cases;
  const failRaw = readRmJson<{ cases: Fail[] }>("research/ax-failure-cases.json").cases;
  const publicCases: PublicCase[] = pubRaw.map((c) => ({ id: c.id, org: c.organization, w: c.workflow.ko, ind: c.industry, region: c.region, stage: c.deployment_stage, verify: c.outcome_verification }));
  const failures: FailureCase[] = failRaw.map((c) => ({ id: c.id, org: c.organization, domain: c.domain.ko, change: c.attempted_change.ko, outcome: c.outcome, causes: c.failure_causes, check: c.capstone_check.ko }));

  /* 실무 템플릿: README 표의 "언제"와 toolkit 목록 */
  const whenRows = table(between(readme, "## 실무 템플릿", "현업·리더"));
  const tk = readRm("toolkit/README.md");
  const templates: Template[] = [...between(tk, "## 목록", "\n## ").matchAll(/^- \[([^\]]+)\]\(([a-z0-9-]+\.md)\)/gm)].map((m) => ({
    slug: m[2].replace(/\.md$/, ""),
    t: m[1],
    path: `toolkit/${m[2]}`,
    when: whenRows.find(([, items]) => items.includes(`[${m[1]}]`))?.[0] ?? "",
  }));

  /* 월간 채용 현황 */
  const hb = between(readme, "<!-- hiring-monthly:start -->", "<!-- hiring-monthly:end -->");
  const hiring = {
    lede: strip(hb.trim().split("\n\n")[0]),
    rows: table(hb).map(([type, n, open]) => ({ type, n: +n, open: +open })) as HiringRow[],
    note: "재게시와 프로젝트 공고가 섞여 있어 고유 채용 수는 아니에요.",
    months: fs.existsSync(path.join(RM, "research/hiring-monthly"))
      ? fs.readdirSync(path.join(RM, "research/hiring-monthly")).filter((f) => /^\d{4}-\d{2}\.json$/.test(f)).sort().map((f) => f.replace(".json", ""))
      : [],
  };
  const hiringTotal = hiring.rows.reduce((a, r) => a + r.n, 0);

  return { version, commit, date, defn, role, start, faq, stages, topics, cases, publicCases, failures, templates, hiring, hiringTotal };
}

export function topicBySlug(slug: string) {
  const t = roadmap().topics.find((x) => x.slug === slug);
  if (!t) throw new Error(`없는 로드맵 주제 ${slug}`);
  return t;
}

/** 로드맵 레포 안 링크(문서 기준 상대 경로)를 사이트 주소나 GitHub 주소로 바꿔요. */
export function mapRoadmapLink(fromFile: string, href: string): string {
  if (/^([a-z]+:|#|\/\/)/i.test(href)) return href;
  const [p, hash = ""] = href.split("#");
  const h = hash ? `#${hash}` : "";
  if (!p) return h;
  const rel = path.posix.normalize(path.posix.join(path.posix.dirname(fromFile), decodeURI(p))).replace(/\/$/, "");
  const r = roadmap();
  const topic = r.topics.find((t) => t.path === rel);
  if (topic) return `/roadmap/${topic.slug}/${h}`;
  const cs = r.cases.find((c) => c.path === rel || c.path === `${rel}/README.md`);
  if (cs) return `/library/cases/${cs.id}/${h}`;
  const tp = r.templates.find((t) => t.path === rel);
  if (tp) return `/library/templates/${tp.slug}/${h}`;
  if (rel === "start-here/non-developer-glossary.md") return `/glossary/${h}`;
  if (rel === "case-studies/README.md" || rel === "case-studies") return `/library/${h}`;
  if (rel === "research/public-ax-cases.md") return `/library/public/${h}`;
  if (rel === "research/ax-failure-cases.md") return `/library/failures/${h}`;
  if (rel === "toolkit/README.md" || rel === "toolkit") return `/library/templates/${h}`;
  if (rel.startsWith("research/hiring-monthly")) return `/library/jobs/${h}`;
  if (rel === "README.md") return `/roadmap/${h}`;
  const isDir = fs.existsSync(path.join(RM, rel)) && fs.statSync(path.join(RM, rel)).isDirectory();
  return `${ROADMAP_URL}/${isDir ? "tree" : "blob"}/main/${encodeURI(rel)}${h}`;
}
