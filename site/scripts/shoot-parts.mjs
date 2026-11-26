// 챕터 화면 "구성" 카드에 넣을 파트 첫 장 그림을 찍어요.
// 챕터는 assets/parts/<폴더>/<쪽>.jpg, 꿀팁은 assets/parts/extras/<폴더>/<쪽>.jpg 예요. 1쪽은 표지예요.
// 덱이나 README 구성 표를 고쳤을 때 쳐요: node scripts/shoot-parts.mjs [폴더 이름...]
// 그림 속 "KANT AX/AI 엔지니어 트랙"은 shoot-covers.mjs처럼 사이트 이름으로 바꿔 찍어요.
// 크기: 480x270(무대 1920x1080의 1/4), JPEG 품질 78. 카드가 PC에서 240px 안팎이라 레티나에서도 또렷하고, 한 장 20KB 안팎이에요.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const SITE = path.resolve(import.meta.dirname, "..");
const ROOT = path.resolve(SITE, "..");
const OUT = path.join(SITE, "assets", "parts");
const cur = JSON.parse(fs.readFileSync(path.join(ROOT, "curriculum.json"), "utf8"));
const only = process.argv.slice(2);

/** README "구성" 표에서 파트마다 첫 쪽을 꺼내요(lib/chapter.ts의 chapterInfo와 같은 규칙) */
function firstPages(readme) {
  const md = fs.readFileSync(readme, "utf8");
  const sec = (md.split(/^## /m).find((x) => x.startsWith("구성")) ?? "").split("\n").slice(1);
  return sec
    .filter((l) => l.startsWith("|"))
    .slice(2)
    .map((l) => l.split("|").slice(1, -1).map((x) => x.trim()))
    .filter((r) => r.length >= 2 && /\d/.test(r[1]))
    .map((r) => parseInt(r[1], 10));
}

const jobs = [
  ...cur.chapters.map((c) => ({ dir: c.dir, src: path.join(ROOT, c.dir), slides: c.slides, out: path.join(OUT, c.dir) })),
  ...cur.extras.map((e) => ({ dir: e.dir, src: path.join(ROOT, "extras", e.dir), slides: e.slides, out: path.join(OUT, "extras", e.dir) })),
].filter((j) => !only.length || only.includes(j.dir));

function fix() {
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) if (/KANT/.test(n.nodeValue)) n.nodeValue = n.nodeValue.replace(/KANT AX\/AI 엔지니어 트랙/g, "풀스택 AI/AX 엔지니어").replace(/KANT\s*/g, "");
  document.querySelectorAll("[class*=toast],[class*=hint],[class*=fs-tip]").forEach((e) => e.remove());
}

const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 0.25 });
await ctx.addInitScript(() => {
  try {
    localStorage.setItem("slides-anim", "off");
  } catch {}
});
const p = await ctx.newPage();
let shots = 0;
for (const j of jobs) {
  const pages = [...new Set([1, ...firstPages(path.join(j.src, "README.md"))])].sort((a, b) => a - b);
  fs.rmSync(j.out, { recursive: true, force: true });
  fs.mkdirSync(j.out, { recursive: true });
  for (const n of pages) {
    await p.goto("about:blank");
    await p.goto(`file://${path.join(j.src, j.slides)}#${n}`);
    await p.waitForTimeout(700);
    await p.evaluate(fix);
    // 플레이어 단추와 막대, 안내, 복사 아이콘은 그림에서 빼요(무대 #pl-stage만 남겨요)
    await p.evaluate(() => document.querySelectorAll("[id^=pl-]:not(#pl-stage), .pl-copy").forEach((e) => (e.style.visibility = "hidden")));
    await p.screenshot({ path: path.join(j.out, `${n}.jpg`), type: "jpeg", quality: 78 });
    shots++;
  }
  console.log("parts", j.dir, pages.join(","));
}
await b.close();
console.log(`shoot-parts: ${shots}장`);
