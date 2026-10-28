// Exports every slide in deck.json order to a single PDF (one 1920x1080 page per slide).
// Usage: node tools/export.js slides git-basics-slides.pdf
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const [dir, out] = process.argv.slice(2);
const deck = JSON.parse(fs.readFileSync(path.join(dir, 'deck.json'), 'utf8'));
const iconDir = path.join(__dirname, 'icons');
const icons = {};
for (const f of fs.readdirSync(iconDir).filter(f => f.endsWith('.svg'))) {
  icons[f.replace('.svg', '')] = fs.readFileSync(path.join(iconDir, f), 'utf8')
    .replace(/<!--.*?-->/s, '').replace(/\s(width|height|class)="[^"]*"/g, '').trim();
}
const head = `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=JetBrains+Mono:wght@400;700&display=swap">
<style>
@page{size:1920px 1080px;margin:0}
html,body{margin:0;padding:0}
section{position:relative;width:1920px;height:1080px;box-sizing:border-box;overflow:hidden;break-after:page}
section *{box-sizing:border-box}
p,h1,h2,h3,ul,ol{margin:0}
h1{font-size:96px;font-weight:600;line-height:1.1} h2{font-size:64px;font-weight:600;line-height:1.15} h3{font-size:44px;font-weight:600;line-height:1.2} p{font-size:32px;line-height:1.4}
x-icon,x-shape{display:block;flex:none}
x-icon svg,x-shape svg{display:block;width:100%;height:100%}
x-shape[kind=ellipse]{border-radius:50%}
table{border-collapse:collapse;width:100%}
td,th{padding:0.35em 0.6em;text-align:left;border-bottom:1px solid #ccc;vertical-align:top}
aside{display:none}
</style></head><body>`;
(async () => {
  const body = deck.order.map(id => fs.readFileSync(path.join(dir, id + '.html'), 'utf8')).join('\n');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.setContent(head + body + '</body></html>', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(icons => {
    for (const el of document.querySelectorAll('x-icon')) el.innerHTML = icons[el.getAttribute('name')] || '';
    for (const el of document.querySelectorAll('x-shape[kind^=arrow]')) {
      const fill = getComputedStyle(el).backgroundColor;
      el.style.background = 'none';
      const pts = el.getAttribute('kind') === 'arrow-left' ? '100,30 40,30 40,0 0,50 40,100 40,70 100,70' : '0,30 60,30 60,0 100,50 60,100 60,70 0,70';
      el.innerHTML = `<svg viewBox="0 0 100 100" preserveAspectRatio="none"><polygon points="${pts}" fill="${fill}"/></svg>`;
    }
    for (const el of document.querySelectorAll('x-connector')) {
      const cs = getComputedStyle(el);
      const [x1, y1, x2, y2] = ['x1', 'y1', 'x2', 'y2'].map(a => +el.getAttribute(a));
      const w = parseFloat(el.style.borderWidth) || 3;
      const dash = (el.style.borderStyle || '').includes('dash') ? `stroke-dasharray="${w * 3} ${w * 2}"` : '';
      const ang = Math.atan2(y2 - y1, x2 - x1), h = w * 4;
      const head = el.getAttribute('head') === 'end'
        ? `<polygon points="${x2},${y2} ${x2 - h * Math.cos(ang - 0.45)},${y2 - h * Math.sin(ang - 0.45)} ${x2 - h * Math.cos(ang + 0.45)},${y2 - h * Math.sin(ang + 0.45)}" fill="${cs.color}"/>` : '';
      const ex = head ? x2 - h * 0.8 * Math.cos(ang) : x2, ey = head ? y2 - h * 0.8 * Math.sin(ang) : y2;
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('style', 'position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible');
      svg.innerHTML = `<line x1="${x1}" y1="${y1}" x2="${ex}" y2="${ey}" stroke="${cs.color}" stroke-width="${w}" ${dash}/>${head}`;
      el.replaceWith(svg);
    }
  }, icons);
  await page.pdf({ path: out, width: '1920px', height: '1080px', printBackground: true });
  await browser.close();
  console.log(`${deck.order.length} slides -> ${out}`);
})();
