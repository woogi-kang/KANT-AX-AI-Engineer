// Renders every slide at 1920x1080 and saves the box of each element with an id to tools/rects.json.
// gen.py reads it to put rings, underlines and leader lines exactly on labels whose width depends on the font.
// Usage (from the chapter folder): python3 tools/gen.py slides && node tools/measure.js slides && python3 tools/gen.py slides
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const dir = process.argv[2];
const head = `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=JetBrains+Mono:wght@400;700&display=swap">
<style>html,body{margin:0}section{position:relative;width:1920px;height:1080px;box-sizing:border-box;overflow:hidden}
section *{box-sizing:border-box}p,h1,h2,h3{margin:0}x-icon,x-shape{display:block}aside{display:none}</style></head><body>`;
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  const out = {};
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort()) {
    await page.setContent(head + fs.readFileSync(path.join(dir, f), 'utf8') + '</body></html>', { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    out[f.replace('.html', '')] = await page.evaluate(() => {
      const S = document.querySelector('section').getBoundingClientRect(), o = {};
      for (const el of document.querySelectorAll('section [id]')) {
        const r = el.getBoundingClientRect();
        o[el.id] = [r.left - S.left, r.top - S.top, r.width, r.height].map(v => Math.round(v));
      }
      return o;
    });
  }
  await browser.close();
  fs.writeFileSync(path.join(__dirname, 'rects.json'), JSON.stringify(out, null, 0).replace(/\},"/g, '},\n"'));
  console.log('rects.json:', Object.keys(out).length, 'slides');
})();
