// 사이트 전체 검수: npm run build 뒤 out/을 띄우고(cd out && python3 -m http.server 8766) node scripts/qa.cjs [주소 일부]
// 모든 화면을 1440, 390 폭으로 열어 가로 넘침, 콘솔 오류, 깨진 내부 링크, 깨진 그림을 찾아요. SHOT=폴더 를 주면 화면을 찍어요.
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const OUT = path.resolve(__dirname, "..", "out");
const BASE = process.env.BASE || "http://localhost:8766";
const SHOT = process.env.SHOT; // 폴더를 주면 스크린샷
const only = process.argv[2];
const pages = [];
(function walk(d) { for (const f of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, f.name); if (f.isDirectory()) { if (!/^(decks|design|img|_next|updates\/.*img)$/.test(f.name)) walk(p); } else if (f.name === "index.html") pages.push("/" + path.relative(OUT, d) + (d === OUT ? "" : "/")); } })(OUT);
const exists = (u) => { const p = u.split("#")[0].split("?")[0]; if (!p.startsWith("/")) return true; const f = path.join(OUT, decodeURIComponent(p)); return fs.existsSync(f) && (fs.statSync(f).isFile() || fs.existsSync(path.join(f, "index.html"))); };
(async () => {
  const b = await chromium.launch();
  const list = pages.map((p) => p.replace("//", "/")).filter((p) => !only || p.includes(only)).sort();
  let bad = 0; const broken = new Set();
  for (const w of [1440, 390]) {
    const ctx = await b.newContext({ viewport: { width: w, height: w > 500 ? 900 : 844 }, deviceScaleFactor: 1 });
    const pg = await ctx.newPage();
    const errs = []; pg.on("pageerror", (e) => errs.push(e.message)); pg.on("console", (m) => m.type() === "error" && errs.push(m.text()));
    for (const u of list) {
      errs.length = 0;
      await pg.goto(BASE + u, { waitUntil: "networkidle" });
      const r = await pg.evaluate(() => {
        const sw = document.documentElement.scrollWidth, cw = document.documentElement.clientWidth;
        const wide = [...document.querySelectorAll("body *")].filter((e) => { const b = e.getBoundingClientRect(); if (!b.width) return false; let p = e.parentElement; while (p) { const s = getComputedStyle(p).overflowX; if (s === "auto" || s === "scroll" || s === "hidden") return false; p = p.parentElement; } return b.right > cw + 1; }).slice(0, 3).map((e) => e.tagName + "." + e.className + " " + Math.round(e.getBoundingClientRect().right));
        const imgs = [...document.images].filter((i) => i.complete && i.naturalWidth === 0 && i.loading !== "lazy").map((i) => i.src);
        const hrefs = [...document.querySelectorAll("a[href]")].map((a) => a.getAttribute("href"));
        return { sw, cw, wide, imgs, hrefs };
      });
      const dead = r.hrefs.filter((h) => h && h.startsWith("/") && !exists(h));
      dead.forEach((d) => broken.add(u + " -> " + d));
      const prob = [];
      if (r.sw > r.cw + 1) prob.push(`가로 넘침 ${r.sw}>${r.cw} ${r.wide.join(" | ")}`);
      if (r.imgs.length) prob.push("깨진 그림 " + r.imgs.join(" "));
      if (errs.length) prob.push("오류 " + [...new Set(errs)].slice(0, 2).join(" / "));
      if (prob.length) { bad++; console.log(`[${w}] ${u}\n   ` + prob.join("\n   ")); }
      if (SHOT) { fs.mkdirSync(SHOT, { recursive: true }); await pg.screenshot({ path: path.join(SHOT, `${(u.replace(/\//g, "_") || "_home").replace(/^_|_$/g, "") || "home"}-${w}.png`), fullPage: true }); }
    }
    await ctx.close();
  }
  console.log(`검수: 화면 ${list.length}개 × 폭 2 = ${list.length * 2}번, 문제 ${bad}건, 깨진 내부 링크 ${broken.size}개`);
  [...broken].slice(0, 30).forEach((x) => console.log("  링크 " + x));
  await b.close();
})();
