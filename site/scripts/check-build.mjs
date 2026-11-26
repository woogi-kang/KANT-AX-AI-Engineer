// 빌드가 끝나면 페이지가 빠짐없이 생겼는지 세요. 하나라도 없으면 실패로 끝나요.
import fs from "node:fs";
import path from "node:path";

const SITE = path.resolve(import.meta.dirname, "..");
const OUT = path.join(SITE, "out");
const cur = JSON.parse(fs.readFileSync(path.join(SITE, "..", "curriculum.json"), "utf8"));
const need = [
  "index.html",
  "404.html",
  "updates/index.html",
  "legal/index.html",
  "design/index.html",
  ...cur.chapters.map((c) => `chapters/${c.dir}/index.html`),
  ...cur.chapters.map((c) => `decks/${c.dir}/${c.slides}`),
  ...cur.chapters.map((c) => `decks/${c.dir}/${c.slides.replace(/\.html$/, ".pdf")}`),
  ...cur.extras.map((e) => `extras/${e.dir}/index.html`),
  ...cur.extras.map((e) => `decks/extras/${e.dir}/${e.slides}`),
  ...cur.updates.map((u) => `updates/${u.dir}/index.html`),
];
const missing = need.filter((p) => !fs.existsSync(path.join(OUT, p)));
if (missing.length) {
  console.error(`check-build: 없는 파일 ${missing.length}개\n` + missing.map((m) => "  " + m).join("\n"));
  process.exit(1);
}
console.log(`check-build: 챕터 ${cur.chapters.length}개, 번외 ${cur.extras.length}개, 릴리스 노트 ${cur.updates.length}개, 파일 ${need.length}개가 모두 있어요`);
