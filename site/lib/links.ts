// 로드맵 주제와 강의 챕터를 잇는 표(content/roadmap-links.json)를 읽어요.
import fs from "node:fs";
import path from "node:path";
import { load } from "./content";
import { roadmap } from "./roadmap";

type Entry = { chapters: string[]; know?: string[][]; soon?: string };
let cache: { byTopic: Record<string, Entry>; usedBy: Record<string, string[]> } | null = null;

export function links() {
  if (cache) return cache;
  const raw = JSON.parse(fs.readFileSync(path.join(process.cwd(), "content", "roadmap-links.json"), "utf8")) as { topics: Record<string, Entry> };
  const nos = new Set(load().chapters.map((c) => c.no));
  const slugs = new Set(roadmap().topics.map((t) => t.slug));
  const usedBy: Record<string, string[]> = {};
  for (const [slug, e] of Object.entries(raw.topics)) {
    if (!slugs.has(slug)) throw new Error(`roadmap-links.json: 로드맵에 없는 주제 ${slug}`);
    for (const n of [...e.chapters, ...(e.know ?? []).flat()]) if (!nos.has(n)) throw new Error(`roadmap-links.json: ${slug}에 없는 챕터 ${n}`);
    for (const n of e.chapters) (usedBy[n] ??= []).push(slug);
  }
  cache = { byTopic: raw.topics, usedBy };
  return cache;
}

/** 주제에 붙은 챕터 번호(없으면 빈 배열) */
export const topicChapters = (slug: string) => links().byTopic[slug]?.chapters ?? [];
/** 챕터를 쓰는 로드맵 주제 주소들 */
export const chapterTopics = (no: string) => links().usedBy[no] ?? [];
