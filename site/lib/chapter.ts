// 챕터 README에서 학습 목표, 구성(파트와 쪽), 절을 꺼내요.
import fs from "node:fs";
import path from "node:path";
import { ROOT } from "./content";

export type Part = { name: string; from: number; to: number; desc: string };

function readmeOf(relDir: string) {
  return fs.readFileSync(path.join(ROOT, relDir, "README.md"), "utf8");
}
const sect = (md: string, name: string) => (md.split(/^## /m).find((x) => x.startsWith(name)) ?? "").split("\n").slice(1).join("\n").trim();
const rows = (md: string) =>
  md
    .split("\n")
    .filter((l) => l.startsWith("|"))
    .slice(2)
    .map((l) => l.split("|").slice(1, -1).map((x) => x.trim()));

export function chapterInfo(relDir: string) {
  const md = readmeOf(relDir);
  const goals = sect(md, "학습 목표")
    .split("\n")
    .filter((l) => l.startsWith("- "))
    .map((l) => l.slice(2));
  const parts: Part[] = rows(sect(md, "구성"))
    .filter((r) => r.length >= 2 && /\d/.test(r[1]))
    .map(([name, range, desc = ""]) => {
      const [a, b] = range.split(/[–~-]/).map((x) => parseInt(x, 10));
      return { name: name.replace(/^\d+\s*(?:\.|·)\s*/, ""), from: a, to: b || a, desc };
    });
  return { goals, parts };
}

/** 렌더한 README HTML을 h2 절로 나눠요: [{id, title, html}] */
export function splitSections(html: string) {
  const out: { id: string; title: string; html: string }[] = [];
  const re = /<h2 id="([^"]*)">([\s\S]*?)<\/h2>/g;
  const marks = [...html.matchAll(re)];
  marks.forEach((m, n) => {
    const start = (m.index ?? 0) + m[0].length;
    const end = n + 1 < marks.length ? marks[n + 1].index : html.length;
    out.push({ id: m[1], title: m[2].replace(/<[^>]+>/g, ""), html: html.slice(start, end) });
  });
  return out;
}
