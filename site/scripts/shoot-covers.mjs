// 덱 표지를 사이트용 그림(assets/covers/NN.jpg, 꿀팁은 x-폴더.jpg)으로 찍어요.
// 새 챕터나 꿀팁을 더했을 때 한 번 쳐요: node scripts/shoot-covers.mjs [폴더 이름...]
// 표지의 "KANT AX/AI 엔지니어 트랙"은 사이트 이름으로 바꿔 찍어요(사이트에는 KANT를 쓰지 않아요).
// 플레이어와 같은 Chromium이 있어야 해요(require('playwright')).
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const SITE = path.resolve(import.meta.dirname, "..");
const ROOT = path.resolve(SITE, "..");
const OUT = path.join(SITE, "assets", "covers");
const cur = JSON.parse(fs.readFileSync(path.join(ROOT, "curriculum.json"), "utf8"));
const only = process.argv.slice(2);

const jobs = [
  ...cur.chapters.map((c) => ({ dir: c.dir, file: path.join(ROOT, c.dir, c.slides), out: `${c.dir.slice(0, 2)}.jpg` })),
  ...cur.extras.map((e) => ({ dir: e.dir, file: path.join(ROOT, "extras", e.dir, e.slides), out: `x-${e.dir}.jpg` })),
].filter((j) => !only.length || only.includes(j.dir));

function fix() {
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) if (/KANT/.test(n.nodeValue)) n.nodeValue = n.nodeValue.replace(/KANT AX\/AI 엔지니어 트랙/g, "풀스택 AI/AX 엔지니어").replace(/KANT\s*/g, "");
  document.querySelectorAll("[class*=toast],[class*=hint],[class*=fs-tip]").forEach((e) => e.remove());
}

const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 0.5 });
await ctx.addInitScript(() => { try { localStorage.setItem("slides-anim", "off"); } catch {} });
const p = await ctx.newPage();
fs.mkdirSync(OUT, { recursive: true });
for (const j of jobs) {
  await p.goto("file://" + j.file);
  await p.waitForTimeout(900);
  await p.evaluate(fix);
  await p.screenshot({ path: path.join(OUT, j.out), type: "jpeg", quality: 82 });
  console.log("cover", j.out);
}
await b.close();
