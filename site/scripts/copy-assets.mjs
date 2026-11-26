// 빌드 전에 레포의 덱 HTML, PDF, 릴리스 노트 그림, 디자인 시안을 public/으로 복사해요.
// 원본은 레포에 있고, 여기서는 복사만 해요.
import fs from "node:fs";
import path from "node:path";

const SITE = path.resolve(import.meta.dirname, "..");
const ROOT = path.resolve(SITE, "..");
const PUB = path.join(SITE, "public");
const cur = JSON.parse(fs.readFileSync(path.join(ROOT, "curriculum.json"), "utf8"));

for (const d of ["decks", "updates", "design"]) fs.rmSync(path.join(PUB, d), { recursive: true, force: true });

let files = 0;
function copy(from, to) {
  if (!fs.existsSync(from)) throw new Error(`없는 파일: ${path.relative(ROOT, from)}`);
  fs.mkdirSync(path.dirname(to), { recursive: true });
  fs.copyFileSync(from, to);
  files++;
}
function deck(srcDir, destDir, slides) {
  copy(path.join(srcDir, slides), path.join(destDir, slides));
  const pdf = slides.replace(/\.html$/, ".pdf");
  copy(path.join(srcDir, pdf), path.join(destDir, pdf));
}

for (const c of cur.chapters) deck(path.join(ROOT, c.dir), path.join(PUB, "decks", c.dir), c.slides);
for (const e of cur.extras) deck(path.join(ROOT, "extras", e.dir), path.join(PUB, "decks", "extras", e.dir), e.slides);
for (const u of cur.updates) {
  const img = path.join(ROOT, "updates", u.dir, "img");
  if (!fs.existsSync(img)) continue;
  for (const f of fs.readdirSync(img)) copy(path.join(img, f), path.join(PUB, "updates", u.dir, "img", f));
}
// 디자인 시안: design/ 폴더를 통째로(만드는 스크립트 .mjs는 빼고)
(function copyDir(from, to) {
  for (const f of fs.readdirSync(from, { withFileTypes: true })) {
    if (f.name.endsWith(".mjs")) continue;
    if (f.isDirectory()) copyDir(path.join(from, f.name), path.join(to, f.name));
    else copy(path.join(from, f.name), path.join(to, f.name));
  }
})(path.join(SITE, "design"), path.join(PUB, "design"));

console.log(`copy-assets: ${files}개 파일을 public/으로 복사했어요`);
