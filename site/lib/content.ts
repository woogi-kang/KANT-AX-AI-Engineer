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
};
type RawExtra = { dir: string; title: string; related: string[]; summary: string; slides: string };
type RawUpdate = { dir: string; date: string; title: string; summary: string };
type RawStage = { title: string; summary: string; groups: { title: string; from: string; to: string }[] };
type Raw = { pages: string; stages: RawStage[]; chapters: RawChapter[]; extras: RawExtra[]; updates: RawUpdate[] };

export type ChapterRef = { dir: string; no: string; title: string };
export type Chapter = RawChapter & {
  no: string;
  trackKey: TrackKey;
  stageNo: number;
  stageTitle: string;
  groupTitle: string;
  added: string | null;
  prev: ChapterRef | null;
  next: ChapterRef | null;
};
export type Group = { title: string; from: string; to: string; chapters: Chapter[] };
export type Stage = { no: number; title: string; summary: string; groups: Group[]; from: string; to: string; count: number };
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
      no: c.dir.slice(0, 2),
      trackKey: TRACKS[c.track],
      stageNo: 0,
      stageTitle: "",
      groupTitle: "",
      added: gitAddedDate(`${c.dir}/README.md`),
      prev: null,
      next: null,
    };
  });
  const ref = (c: Chapter): ChapterRef => ({ dir: c.dir, no: c.no, title: c.title });
  chapters.forEach((c, i) => {
    c.prev = i > 0 ? ref(chapters[i - 1]) : null;
    c.next = i < chapters.length - 1 ? ref(chapters[i + 1]) : null;
  });

  const stages: Stage[] = raw.stages.map((s, si) => {
    const groups = s.groups.map((g) => {
      const list = chapters.filter((c) => c.no >= g.from && c.no <= g.to);
      for (const c of list) {
        if (c.stageNo) throw new Error(`${c.dir}: 묶음 두 곳에 들어 있어요`);
        c.stageNo = si + 1;
        c.stageTitle = s.title;
        c.groupTitle = g.title;
      }
      return { ...g, chapters: list };
    });
    const from = groups[0].from;
    const to = groups[groups.length - 1].to;
    return {
      no: si + 1,
      title: s.title,
      summary: s.summary,
      groups,
      from,
      to,
      count: groups.reduce((n, g) => n + g.chapters.length, 0),
    };
  });
  const loose = chapters.filter((c) => !c.stageNo).map((c) => c.dir);
  if (loose.length) throw new Error(`단계 묶음에 없는 챕터: ${loose.join(", ")}. curriculum.json의 stages에 넣어 주세요`);

  const byDir = new Map(chapters.map((c) => [c.dir, c]));
  const extras: Extra[] = raw.extras.map((e) => ({
    ...e,
    relatedChapters: e.related.map((d) => {
      const c = byDir.get(d);
      if (!c) throw new Error(`번외 ${e.dir}: 없는 챕터 ${d}`);
      return ref(c);
    }),
  }));

  cache = { pages: raw.pages, stages, chapters, extras, updates: raw.updates };
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
      tag: "릴리스 노트",
    })),
    ...chapters
      .filter((c) => c.added)
      .map((c) => ({
        kind: "chapter" as const,
        date: c.added as string,
        title: `${c.no} · ${c.title}`,
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
