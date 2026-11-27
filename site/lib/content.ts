// 빌드할 때 레포의 curriculum.json, README, 덱 HTML을 읽어 사이트 데이터로 바꿔요.
// 내용은 사이트에서 고치지 않고 레포에서 고쳐요.
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

export const ROOT = path.resolve(process.cwd(), "..");
export const REPO_URL = "https://github.com/woogi-kang/KANT-AX-AI-Engineer";

import { TRACKS, LEVELS, type TrackName, type TrackKey, type LevelName } from "./meta";
export { TRACKS, LEVELS, type TrackName, type TrackKey, type LevelName };

type RawChapter = {
  dir: string;
  title: string;
  track: TrackName;
  goal: string;
  commands?: string;
  slides: string;
  level: LevelName;
  keyword?: string;
  short?: string; // 사이트 목차와 화면에 쓰는 짧은 이름. 없으면 title을 써요
};
type RawExtra = { dir: string; title: string; related: string[]; summary: string; slides: string };
type RawUpdate = { dir: string; date: string; title: string; summary: string };
type RawStage = { title: string; summary: string; groups: { title: string; from: string; to: string }[] };
type RawField = { title: string; icon: string; stages: string[] };
type Raw = { pages: string; fields: RawField[]; stages: RawStage[]; chapters: RawChapter[]; extras: RawExtra[]; updates: RawUpdate[] };

export type ChapterRef = { dir: string; no: string; title: string; seq: number; stageNo: number; stageTitle: string };
export type Chapter = RawChapter & {
  /** 덱과 README의 원래 제목(title은 사이트 이름 short로 바꿔 둬요) */
  deckTitle: string;
  no: string;
  /** 단계 안에서 1부터 세는 사이트 번호(no는 덱 원래 번호) */
  seq: number;
  trackKey: TrackKey;
  stageNo: number;
  stageTitle: string;
  groupTitle: string;
  added: string | null;
  prev: ChapterRef | null;
  next: ChapterRef | null;
};
export type Group = { title: string; from: string; to: string; chapters: Chapter[] };
export type Stage = { no: number; title: string; summary: string; groups: Group[]; from: string; to: string; range: string; count: number };
/** 분야: 단계 여러 개를 묶은 가장 큰 칸(기초, 데이터와 AI, 앞으로 프론트엔드, 백엔드 …) */
export type Field = { no: number; title: string; icon: string; stages: Stage[]; count: number };
export type Extra = RawExtra & { relatedChapters: ChapterRef[] };
export type Update = RawUpdate;
export type NewsItem = {
  kind: "update" | "chapter";
  date: string;
  title: string;
  summary: string;
  href: string;
  tag: string;
};

let cache: {
  pages: string;
  fields: Field[];
  stages: Stage[];
  chapters: Chapter[];
  extras: Extra[];
  updates: Update[];
} | null = null;

function gitAddedDate(rel: string): string | null {
  try {
    const out = execFileSync("git", ["log", "--diff-filter=A", "--format=%as", "--", rel], {
      cwd: ROOT,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
    const lines = out.split("\n").filter(Boolean);
    return lines.length ? lines[lines.length - 1] : null;
  } catch {
    return null;
  }
}

export function load() {
  if (cache) return cache;
  const raw: Raw = JSON.parse(fs.readFileSync(path.join(ROOT, "curriculum.json"), "utf8"));

  const chapters: Chapter[] = raw.chapters.map((c) => {
    if (!(c.track in TRACKS)) throw new Error(`${c.dir}: 모르는 분류 ${c.track}`);
    if (!(c.level in LEVELS)) throw new Error(`${c.dir}: 레벨이 없어요. curriculum.json에 level을 적어 주세요`);
    return {
      ...c,
      title: c.short ?? c.title,
      deckTitle: c.title,
      no: c.dir.slice(0, 2),
      seq: 0,
      trackKey: TRACKS[c.track],
      stageNo: 0,
      stageTitle: "",
      groupTitle: "",
      added: gitAddedDate(`${c.dir}/README.md`),
      prev: null,
      next: null,
    };
  });
  const ref = (c: Chapter): ChapterRef => ({ dir: c.dir, no: c.no, title: c.title, seq: c.seq, stageNo: c.stageNo, stageTitle: c.stageTitle });

  const stages: Stage[] = raw.stages.map((s, si) => {
    let seq = 0;
    const groups = s.groups.map((g) => {
      const list = chapters.filter((c) => c.no >= g.from && c.no <= g.to);
      for (const c of list) {
        if (c.stageNo) throw new Error(`${c.dir}: 묶음 두 곳에 들어 있어요`);
        c.seq = ++seq;
        c.stageNo = si + 1;
        c.stageTitle = s.title;
        c.groupTitle = g.title;
      }
      return { ...g, chapters: list };
    });
    const from = groups[0].from;
    const to = groups[groups.length - 1].to;
    // 번호가 이어지지 않는 단계도 있어요(예: 01–08, 11). 이어진 묶음끼리 "–"로 적어요
    const nos = groups.flatMap((g) => g.chapters.map((c) => parseInt(c.no, 10))).sort((a, b) => a - b);
    const runs: [number, number][] = [];
    for (const n of nos) {
      const last = runs[runs.length - 1];
      if (last && n === last[1] + 1) last[1] = n;
      else runs.push([n, n]);
    }
    const pad = (n: number) => String(n).padStart(2, "0");
    const range = runs.map(([a, b]) => (a === b ? pad(a) : `${pad(a)}–${pad(b)}`)).join(", ");
    return {
      no: si + 1,
      title: s.title,
      summary: s.summary,
      groups,
      from,
      to,
      range,
      count: groups.reduce((n, g) => n + g.chapters.length, 0),
    };
  });
  const loose = chapters.filter((c) => !c.stageNo).map((c) => c.dir);
  if (loose.length) throw new Error(`단계 묶음에 없는 챕터: ${loose.join(", ")}. curriculum.json의 stages에 넣어 주세요`);

  // 이전, 다음은 사이트 순서(단계, 단계 안 번호)로 이어요. 덱 번호로 이으면 단계 사이를 오가요
  const order = [...chapters].sort((a, b) => a.stageNo - b.stageNo || a.seq - b.seq);
  order.forEach((c, i) => {
    c.prev = i > 0 ? ref(order[i - 1]) : null;
    c.next = i < order.length - 1 ? ref(order[i + 1]) : null;
  });

  const byDir = new Map(chapters.map((c) => [c.dir, c]));
  const extras: Extra[] = raw.extras.map((e) => ({
    ...e,
    relatedChapters: e.related.map((d) => {
      const c = byDir.get(d);
      if (!c) throw new Error(`번외 ${e.dir}: 없는 챕터 ${d}`);
      return ref(c);
    }),
  }));

  const used = new Set<string>();
  const fields: Field[] = raw.fields.map((f, fi) => {
    const list = f.stages.map((t) => {
      const s = stages.find((x) => x.title === t);
      if (!s) throw new Error(`분야 ${f.title}: 없는 단계 ${t}`);
      if (used.has(t)) throw new Error(`단계 ${t}가 분야 두 곳에 들어 있어요`);
      used.add(t);
      return s;
    });
    return { no: fi + 1, title: f.title, icon: f.icon, stages: list, count: list.reduce((n, s) => n + s.count, 0) };
  });
  const lost = stages.filter((s) => !used.has(s.title)).map((s) => s.title);
  if (lost.length) throw new Error(`분야에 없는 단계: ${lost.join(", ")}. curriculum.json의 fields에 넣어 주세요`);

  cache = { pages: raw.pages, fields, stages, chapters, extras, updates: raw.updates };
  return cache;
}

export function getChapter(dir: string) {
  const c = load().chapters.find((x) => x.dir === dir);
  if (!c) throw new Error(`없는 챕터 ${dir}`);
  return c;
}

/** 새 소식: 릴리스 노트와 새 챕터를 날짜 순으로 섞어요. */
export function news(): NewsItem[] {
  const { chapters, updates } = load();
  const items: NewsItem[] = [
    ...updates.map((u) => ({
      kind: "update" as const,
      date: u.date,
      title: u.title,
      summary: u.summary,
      href: `/updates/${u.dir}/`,
      tag: "업데이트 노트",
    })),
    ...chapters
      .filter((c) => c.added)
      .map((c) => ({
        kind: "chapter" as const,
        date: c.added as string,
        title: `${c.stageTitle} ${c.seq} · ${c.title}`,
        summary: c.goal,
        href: `/chapters/${c.dir}/`,
        tag: "새 챕터",
      })),
  ];
  return items.sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : a.kind === "update" ? -1 : 1));
}

/** 빌드한 날 기준 7일 안에 처음 올라온 챕터에 "새 챕터" 표시를 달아요. */
export function isNew(c: Chapter, today = new Date()) {
  if (!c.added) return false;
  const days = (today.getTime() - new Date(c.added + "T00:00:00+09:00").getTime()) / 86400000;
  return days < 7;
}

export function deckUrl(dir: string, slides: string, extra = false) {
  return `/decks/${extra ? "extras/" : ""}${dir}/${slides}`;
}
export function pdfUrl(dir: string, slides: string, extra = false) {
  // 수강생이 받는 PDF 링크는 GitHub Pages 주소로 걸어요 (CLAUDE.md 규칙)
  return `${load().pages}/${extra ? "extras/" : ""}${dir}/${slides.replace(/\.html$/, ".pdf")}`;
}

export type SlideInfo = { n: number; id: string; title: string; note: string };

const strip = (h: string) =>
  h
    .replace(/<br\s*\/?>/gi, " ")
    .replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&amp;/g, "&")
    .replace(/\s+/g, " ")
    .trim();

/** 덱 HTML에서 장마다 제목과 발표자 노트를 꺼내요. */
export function slidesOf(file: string): SlideInfo[] {
  const html = fs.readFileSync(path.join(ROOT, file), "utf8");
  const out: SlideInfo[] = [];
  const re = /<section\b([^>]*)>([\s\S]*?)<\/section>/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(html))) {
    const id = /\bid="([^"]+)"/.exec(m[1])?.[1] ?? "";
    const body = m[2];
    const aside = /<aside\b[^>]*>([\s\S]*?)<\/aside>/.exec(body)?.[1] ?? "";
    const noAside = body.replace(/<aside\b[\s\S]*?<\/aside>/g, "");
    const h = /<h([1-3])\b[^>]*>([\s\S]*?)<\/h\1>/.exec(noAside);
    const note = strip(aside);
    out.push({ n: out.length + 1, id, title: h ? strip(h[2]) : note.split(/(?<=요\.)\s/)[0] || id, note });
  }
  return out;
}
