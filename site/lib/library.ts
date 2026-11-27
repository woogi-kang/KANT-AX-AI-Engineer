// 사례와 자료 영역(/library/)이 쓰는 데이터예요. 로드맵 레포(woogi-kang/ax-engineer-roadmap)의
// case.json, research/*.json, 월간 채용 JSON과 문서 표를 읽어요. 값은 레포에 있는 것만 써요.
// 코드값을 한국어로 바꾸는 이름은 레포 문서의 "코드 읽는 법" 표에서 가져오고, 표가 없는 것만 여기 적어요.
import fs from "node:fs";
import path from "node:path";
import { RM, roadmap, readRm, readRmJson, existsRm, sections, strip, type RoadmapCase } from "./roadmap";

/* ---------- 작은 도우미 ---------- */
const rows = (block: string) =>
  block
    .split("\n")
    .filter((l) => /^\|/.test(l) && !/^\|[\s|:-]+\|$/.test(l))
    .slice(1)
    .map((l) => l.replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim()));
const sectionOf = (md: string, title: RegExp) => sections(md).find((s) => title.test(s.title));
const uniq = <T,>(a: T[]) => [...new Set(a)];

/* ---------- 코드 이름(레포 문서 표에 없는 것) ---------- */
/** 산업 코드 → 한국어 (design/plan/data.mjs의 IND와 같아요) */
export const IND_KO: Record<string, string> = {
  "public-sector": "공공",
  manufacturing: "제조",
  "financial-services": "금융",
  "healthcare-social-care": "의료·돌봄",
  "customer-service": "고객 상담",
  collaboration: "협업",
  "software-engineering": "소프트웨어 개발",
  "consumer-retail": "소비재·리테일",
  "legal-life-sciences": "법무·생명과학",
  education: "교육",
  marketing: "마케팅",
  "automotive-service": "자동차 서비스",
  "people-operations": "인사 운영",
  "b2b-sales": "B2B 영업",
  travel: "여행",
  "software-marketing": "소프트웨어 마케팅",
  "professional-services": "전문 서비스",
  "cross-industry": "공통",
};
/** 지역 코드 → 나라 이름 */
export const REGION_KO: Record<string, string> = {
  KR: "한국",
  US: "미국",
  GLOBAL: "글로벌",
  DE: "독일",
  IN_GLOBAL: "인도·글로벌",
  AR: "아르헨티나",
  SE: "스웨덴",
  UK: "영국",
  US_GLOBAL: "미국·글로벌",
  CH: "스위스",
  AU: "호주",
  CA: "캐나다",
};
export const regionKo = (r: string) => REGION_KO[r] ?? r;
export const homeOf = (r: string) => (r === "KR" ? "kr" : "abroad");

/* ---------- 업무 사례 상세 ---------- */
type CaseJson = {
  systems: string[];
  entry_channels: string[];
  current_autonomy: string;
  designed_autonomy: string;
  implemented_project_stages: number[];
  designed_project_stages: number[];
  verified_at: string;
  recommended_after: string[];
  learning_order: number;
  status: string;
};
export type Boundary = { label: string; write: string; autonomy: string; p: string };
export type CaseDetail = RoadmapCase & {
  json: CaseJson;
  boundary: Boundary[];
  intro: string;
  failureNote: string;
  limits?: { title: string; body: string };
  rest: { title: string; body: string }[];
  runbook?: { path: string; run: string[]; test: string[]; rest: { title: string; body: string }[] };
  summary?: { input: number; proposals: number; passed: boolean; status: Record<string, number>; topics: Record<string, number>; asOf: string };
  dashboard?: string;
  publicIds: string[];
  failureIds: string[];
};

/** A0~A4 뜻 (delivery-lifecycle/05-execution-contracts.md "자율성 수준" 표) */
export function autonomyLevels() {
  const md = readRm("delivery-lifecycle/05-execution-contracts.md");
  return rows(sectionOf(md, /^자율성 수준/)?.body ?? "").map(([lv, ai, run]) => ({ lv, ai, run }));
}
/** P1~P5 이름 (projects/README.md 그림) */
export function projectStages() {
  const md = readRm("projects/README.md");
  return [...md.matchAll(/P(\d)\["\d\. ([^"]+)"\]/g)].map((m) => ({ no: +m[1], t: m[2] }));
}
/** "A1-A3", "A0" → [1,2,3], [0] */
export const autonomyRange = (s: string) => {
  const m = /A(\d)(?:\s*[-–~]\s*A(\d))?/.exec(s);
  if (!m) return [];
  const a = +m[1];
  const b = m[2] ? +m[2] : a;
  return Array.from({ length: b - a + 1 }, (_, k) => a + k);
};

const codeBlocks = (s: string) => [...s.matchAll(/```[a-z]*\n([\s\S]*?)```/g)].map((m) => m[1].trim());

export function caseDetail(id: string): CaseDetail {
  const c = roadmap().cases.find((x) => x.id === id);
  if (!c) throw new Error(`없는 업무 사례 ${id}`);
  const dir = `case-studies/${id}`;
  const json = readRmJson<CaseJson>(`${dir}/case.json`);
  const md = readRm(c.path).replace(/^# .+\n+/m, "");
  const bnd = /<!-- case-boundary:start -->([\s\S]*?)<!-- case-boundary:end -->/.exec(md)?.[1] ?? "";
  const boundary = rows(bnd).map(([label, write, autonomy, p]) => ({ label, write, autonomy, p }));
  const after = md.replace(/<!-- case-boundary:start -->[\s\S]*?<!-- case-boundary:end -->\n*/, "");
  const head = after.split(/\n(?=## )/)[0];
  const failureNote = /<!-- failure-cases:start -->([\s\S]*?)<!-- failure-cases:end -->/.exec(head)?.[1]?.trim() ?? "";
  const intro = head.replace(/<!-- failure-cases:start -->[\s\S]*?<!-- failure-cases:end -->/, "").trim();
  const secs = sections("\n" + after);
  const limits = secs.find((s) => /한계/.test(s.title));
  const rest = secs.filter((s) => s !== limits);

  let runbook: CaseDetail["runbook"];
  if (existsRm(`${dir}/RUNBOOK.md`)) {
    const rb = readRm(`${dir}/RUNBOOK.md`);
    const rs = sections(rb);
    const run = sectionOf(rb, /^실행/);
    const test = sectionOf(rb, /^테스트/);
    runbook = {
      path: `${dir}/RUNBOOK.md`,
      run: run ? codeBlocks(run.body) : [],
      test: test ? codeBlocks(test.body) : [],
      rest: rs.filter((s) => s.title !== run?.title && s.title !== test?.title),
    };
  }
  let summary: CaseDetail["summary"];
  if (existsRm(`${dir}/artifacts/run-summary.json`)) {
    const s = readRmJson<{ input_count: number; proposal_count: number; evaluation_passed: boolean; status_counts: Record<string, number>; topic_counts: Record<string, number>; as_of: string }>(`${dir}/artifacts/run-summary.json`);
    summary = { input: s.input_count, proposals: s.proposal_count, passed: s.evaluation_passed, status: s.status_counts, topics: s.topic_counts, asOf: s.as_of.slice(0, 10) };
  }
  let dashboard: string | undefined;
  const png = path.join(RM, dir, "artifacts/dashboard.png");
  if (fs.existsSync(png)) dashboard = `data:image/png;base64,${fs.readFileSync(png).toString("base64")}`;

  const lib = library();
  return {
    ...c,
    json,
    boundary,
    intro,
    failureNote,
    limits,
    rest,
    runbook,
    summary,
    dashboard,
    publicIds: lib.pub.filter((p) => p.related.includes(id)).map((p) => p.id),
    failureIds: lib.fails.filter((f) => f.related.includes(id)).map((f) => f.id),
  };
}

/* ---------- 공개 사례, 실패·중단 사례, 채용 ---------- */
export type PubCase = {
  id: string;
  region: string;
  org: string;
  w: string;
  ind: string;
  stage: string;
  verify: string;
  source: string;
  checked: string;
  urls: string[];
  related: string[];
  /** public-ax-cases.md의 그 사례 절 */
  md: string;
  /** 절의 굵은 이름 목록(- **문제**: …) */
  parts: { label: string; md: string }[];
  /** 목록 뒤에 붙은 추가 확인, 정정, 원문 대조 문단 */
  notes: { kind: string; tag: string; md: string }[];
};

/** 사례 절을 굵은 이름 목록과 뒤에 붙은 확인 문단으로 나눠요. */
function splitPub(md: string) {
  const parts: { label: string; md: string }[] = [];
  const notes: { kind: string; tag: string; md: string }[] = [];
  for (const block of md.split(/\n\s*\n/)) {
    const b = block.trim();
    if (!b) continue;
    if (/^- \*\*/.test(b)) {
      for (const line of b.split("\n")) {
        const m = /^- \*\*(.+?)\*\*\s*:?\s*(.*)$/.exec(line);
        if (m) parts.push({ label: m[1].replace(/:$/, ""), md: m[2] });
        else if (parts.length) parts[parts.length - 1].md += " " + line.trim();
      }
      continue;
    }
    const m = /^([가-힣 ]+?) `([^`]+)`\s*(.*)$/s.exec(b);
    if (m) notes.push({ kind: m[1].trim(), tag: m[2], md: m[3].replace(/^:\s*/, "") });
    else notes.push({ kind: "", tag: "", md: b });
  }
  return { parts, notes };
}

/* ---------- 조직 로고 ---------- */
/**
 * 사례 번호 → Simple Icons(CC0) 아이콘 이름. 조직의 공식 브랜드 마크가 Simple Icons에 있을 때만 적어요.
 * LG유플러스는 LG 그룹 심벌을, 삼성SDS는 삼성 워드마크를, GE Appliances는 GE 마크를 같이 써요.
 * 없는 조직은 첫 글자(공공기관은 건물 아이콘)로 대신해요. 상표는 각 소유자의 것이에요.
 */
export const ORG_LOGO: Record<string, string> = {
  K04: "lg",
  K07: "lg",
  K10: "lg",
  K16: "lg",
  K05: "samsung",
  G03: "siemens",
  G05: "bosch",
  G10: "accenture",
  G15: "klarna",
  G16: "virginatlantic",
  G17: "zapier",
  G23: "generalelectric",
  FK03: "samsung",
  FG01: "mcdonalds",
  FG02: "aircanada",
  FG07: "replit",
  FG08: "cnet",
  FG10: "zillow",
};
/** 도입 단계 배지 색: 운영은 초록, 제한 운영·시범은 파랑, 그 밖은 회색 */
export const stageTone = (s: string) => (s === "operation" ? "ok" : s === "limited-operation" || s === "pilot" ? "ac" : "");
/** 성과 검증 배지 색 */
export const verifyTone = (v: string) => (v === "cross-checked" ? "ok" : v === "self-reported" ? "warn" : "");
export const isPublicOrg = (org: string) => /위원회|교육부|노동부|Department|Bundesagentur|City|시$/.test(org.replace(/\s*\([^)]*\)\s*/g, ""));
export type FailCase = {
  id: string;
  region: string;
  org: string;
  domain: string;
  change: string;
  metric: string;
  happened: string;
  outcome: string[];
  causes: string[];
  evidence: string;
  check: string;
  disclosed: string;
  sources: { url: string; publisher: string; published: string; checked: string; supports: string }[];
  limits: string[];
  related: string[];
};

let cache: ReturnType<typeof build> | null = null;
export function library() {
  return (cache ??= build());
}

function build() {
  /* 공개 사례 */
  type Ko = { ko: string };
  type Claim = { checked_at: string | null; source_urls: string[] };
  type Pub = { id: string; region: string; organization: string; workflow: Ko; industry: string; source_type: string; deployment_stage: string; outcome_verification: string; source_urls: string[]; related_cases?: string[]; claims: Claim[] };
  const pj = readRmJson<{ verified_at: string; updated_at: string; cases: Pub[] }>("research/public-ax-cases.json");
  const pmd = readRm("research/public-ax-cases.md");
  const pubSec = (id: string) => {
    const m = new RegExp(`\\n### ${id}\\. [^\\n]*\\n([\\s\\S]*?)(?=\\n### |\\n## |$)`).exec(pmd);
    return m ? m[1].trim() : "";
  };
  // "근거를 읽는 세 축" 표: 출처, 도입, 성과의 코드와 뜻
  const axes = rows(sectionOf(pmd, /^근거를 읽는 세 축/)?.body ?? "").map(([axis, codes, mean]) => {
    const cs = [...codes.matchAll(/`([A-Z_]+)`/g)].map((m) => m[1]);
    const ms = mean.split(" / ").map((x) => x.trim());
    return { axis, pairs: cs.map((c, k) => [c, ms[k] ?? c] as [string, string]) };
  });
  const axisKo = (axis: string, code: string) => axes.find((a) => a.axis === axis)?.pairs.find(([c]) => c === code)?.[1] ?? code;
  // JSON 코드 → 문서 코드
  const STAGE_CODE: Record<string, string> = { pilot: "PILOT", "limited-operation": "LIMITED", operation: "LIVE", expanding: "EXPANDING", "adjusted-operation": "ADJUSTED", unknown: "UNKNOWN" };
  const VERIFY_CODE: Record<string, string> = { none: "NONE", "self-reported": "SELF", "cross-checked": "CROSS", independent: "INDEPENDENT" };
  const SOURCE_CODE: Record<string, string> = { "organization-official": "ORG", "joint-official": "JOINT", "vendor-customer-case": "VENDOR", "mixed-official-independent": "MIXED", "government-report": "GOV" };
  const pub: PubCase[] = pj.cases.map((c) => {
    const checked = c.claims.map((x) => x.checked_at ?? "").filter(Boolean).sort().at(-1) ?? "";
    return {
      id: c.id,
      region: c.region,
      org: c.organization,
      w: c.workflow.ko,
      ind: c.industry,
      stage: c.deployment_stage,
      verify: c.outcome_verification,
      source: c.source_type,
      checked,
      urls: uniq([...c.source_urls, ...c.claims.flatMap((x) => x.source_urls)]),
      related: c.related_cases ?? [],
      md: pubSec(c.id),
      ...splitPub(pubSec(c.id)),
    };
  });
  const stageKo = (s: string) => axisKo("도입", STAGE_CODE[s] ?? s);
  const verifyKo = (s: string) => axisKo("성과", VERIFY_CODE[s] ?? s);
  const sourceKo = (s: string) => axisKo("출처", SOURCE_CODE[s] ?? s);
  const pubIntro = pmd.split("\n## ")[0];
  const pubMeta = {
    verified: pj.verified_at,
    updated: pj.updated_at,
    baseline: /최초 카탈로그 기준일: `([^`]+)`/.exec(pubIntro)?.[1] ?? "",
    axesMd: sectionOf(pmd, /^근거를 읽는 세 축/)?.body ?? "",
  };

  /* 실패·중단 사례 */
  type Src = { url: string; publisher: string; published_at: string | null; checked_at: string; supports: Ko };
  type Fail = { id: string; region: string; organization: string; domain: Ko; attempted_change: Ko; decision_metric: Ko; what_happened: Ko; outcome: string[]; outcome_disclosed_at: string; failure_causes: string[]; failure_evidence: string; capstone_check: Ko; related_case_studies: string[]; sources: Src[]; limitations: Ko[] };
  const fj = readRmJson<{ checked_at: string; cases: Fail[] }>("research/ax-failure-cases.json");
  const fmd = readRm("research/ax-failure-cases.md");
  const fails: FailCase[] = fj.cases.map((c) => ({
    id: c.id,
    region: c.region,
    org: c.organization,
    domain: c.domain.ko,
    change: c.attempted_change.ko,
    metric: c.decision_metric.ko,
    happened: c.what_happened.ko,
    outcome: c.outcome,
    causes: c.failure_causes,
    evidence: c.failure_evidence,
    check: c.capstone_check.ko,
    disclosed: c.outcome_disclosed_at,
    sources: c.sources.map((s) => ({ url: s.url, publisher: s.publisher, published: s.published_at ?? "", checked: s.checked_at, supports: s.supports.ko })),
    limits: c.limitations.map((l) => l.ko),
    related: c.related_case_studies,
  }));
  const codeRead = sectionOf(fmd, /^코드 읽는 법/)?.body ?? "";
  // 결과 코드 뜻(긴 설명)과 짧은 이름
  const OUT_SHORT: Record<string, string> = { STOPPED: "중단", PAUSED: "일시 중단", SANCTIONED: "제재", SCALED_BACK: "축소", UNPROVEN: "미입증", REVERSED: "되돌림" };
  const outMean = Object.fromEntries(rows(codeRead.split("\n\n")[0]).map(([c, m]) => [c.replace(/`/g, ""), m]));
  const EVID_CODE: Record<string, string> = { "official-record": "RECORD", "self-acknowledged": "ADMITTED", "press-reported": "PRESS" };
  const evidMean = Object.fromEntries(rows(codeRead.split("\n\n").find((b) => /근거 코드/.test(b)) ?? "").map(([c, m]) => [c.replace(/`/g, ""), m]));
  const EVID_SHORT: Record<string, string> = { RECORD: "공적 기록", ADMITTED: "당사자 인정", PRESS: "언론 보도" };
  // 원인 표: `code` 이름 | 뜻 | 수 | 사례
  const causeRows = rows(sectionOf(fmd, /^반복되는 실패 원인/)?.body ?? "").map(([name, mean]) => {
    const m = /`([a-z-]+)`\s*(.+)/.exec(name);
    return { code: m?.[1] ?? name, ko: (m?.[2] ?? name).trim(), mean };
  });
  const causes = uniq(fails.flatMap((f) => f.causes))
    .map((code) => ({ code, ko: causeRows.find((r) => r.code === code)?.ko ?? code, mean: causeRows.find((r) => r.code === code)?.mean ?? "", n: fails.filter((f) => f.causes.includes(code)).length }))
    .sort((a, b) => b.n - a.n || a.ko.localeCompare(b.ko, "ko"));
  // 캡스톤 설계 점검표 여덟 질문
  const capSec = sectionOf(fmd, /^캡스톤 설계에 쓰는 점검표/)?.body ?? "";
  const capstone = [...capSec.matchAll(/^\d+\. (.+)$/gm)].map((m) => {
    const ids = /\(([A-Z0-9, ]+)\)\s*$/.exec(m[1]);
    return { q: strip(m[1].replace(/\s*\([A-Z0-9, ]+\)\s*$/, "")), ids: ids ? ids[1].split(/,\s*/) : [] };
  });
  const capLede = strip(capSec.split("\n\n")[0] ?? "");
  const failMeta = { checked: fj.checked_at, patterns: sectionOf(fmd, /^반복되는 실패 원인/)?.body.split("\n\n").slice(2).join("\n\n") ?? "" };

  /* 월간 채용 현황 */
  type Posting = { id: string; company: string; title_original: string; role_type: string; start_date: string | null; start_basis: string; deadline: string | null; status: string; status_basis: string; employment: string; location: string; experience: string; tags: string[]; url: string | null; possible_duplicate_of?: string | null };
  type Month = { month: string; window: { from: string; to: string }; checked_at: string; queries: string[]; platforms: { name: string; status: string; note: Ko }[]; postings: Posting[]; held: unknown[]; excluded: { reason: string }[] };
  const hdir = path.join(RM, "research/hiring-monthly");
  const months: Month[] = fs.existsSync(hdir)
    ? fs
        .readdirSync(hdir)
        .filter((f) => /^\d{4}-\d{2}\.json$/.test(f))
        .sort()
        .map((f) => readRmJson<Month>(`research/hiring-monthly/${f}`))
    : [];
  const hreadme = readRm("research/hiring-monthly/README.md");
  const hsec = (t: RegExp) => sectionOf(hreadme, t)?.body ?? "";
  // 유형 이름: 2026-10.md 요약에 적힌 이름(AX, AI Agent, FDE)과 같아요
  const ROLE_KO: Record<string, string> = { ax: "AX", "ai-agent": "AI Agent", fde: "FDE" };
  const PLATFORM_KO: Record<string, string> = { jobkorea: "잡코리아", saramin: "사람인", wanted: "원티드", linkedin: "링크드인" };
  const TAG_KO: Record<string, string> = { "project-or-freelance": "프로젝트·프리랜서", "company-undisclosed": "기업명 비공개", "training-matching": "교육기관 매칭" };
  const hiring = months.map((m) => ({
    month: m.month,
    from: m.window.from,
    to: m.window.to,
    checked: m.checked_at,
    queries: m.queries,
    platforms: m.platforms.map((p) => ({ name: PLATFORM_KO[p.name] ?? p.name, collected: p.status === "collected", note: p.note.ko })),
    held: m.held.length,
    excluded: m.excluded.length,
    postings: m.postings.map((p) => ({
      id: p.id,
      company: p.company,
      title: p.title_original,
      role: p.role_type,
      start: p.start_date ?? "",
      deadline: p.deadline ?? "",
      open: p.status === "open",
      status: p.status,
      employment: p.employment,
      location: p.location,
      experience: p.experience,
      tags: p.tags,
      url: p.url,
      dup: p.possible_duplicate_of ?? "",
    })),
  }));

  return {
    pub,
    pubMeta,
    stageKo,
    verifyKo,
    sourceKo,
    stageCode: (s: string) => STAGE_CODE[s] ?? s,
    fails,
    failMeta,
    causes,
    capstone,
    capLede,
    outShort: (c: string) => OUT_SHORT[c] ?? c,
    outMean: (c: string) => outMean[c] ?? "",
    evidShort: (e: string) => EVID_SHORT[EVID_CODE[e]] ?? e,
    evidMean: (e: string) => evidMean[EVID_CODE[e]] ?? "",
    hiring,
    hiringMd: { scope: hsec(/^수집 범위/), roles: hsec(/^직무 범위/), status: hsec(/^분류와 상태/), limits: hsec(/^한계/) },
    ROLE_KO,
    TAG_KO,
  };
}
