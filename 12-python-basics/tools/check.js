// Renders slide sections at 1920x1080 and reports layout problems; saves PNGs.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const [dir, outDir, ...only] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const head = `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=JetBrains+Mono:wght@400;700&display=swap">
<style>
html,body{margin:0;padding:0}
section{position:relative;width:1920px;height:1080px;box-sizing:border-box;overflow:hidden}
section *{box-sizing:border-box}
p,h1,h2,h3,ul,ol{margin:0}
h1{font-size:96px;font-weight:600;line-height:1.1} h2{font-size:64px;font-weight:600;line-height:1.15} h3{font-size:44px;font-weight:600;line-height:1.2} p{font-size:32px;line-height:1.4}
x-icon,x-shape{display:block;background:currentColor}
x-icon{border-radius:6px;opacity:.6}
x-shape[kind=ellipse]{border-radius:50%}
x-connector{display:none}
table{border-collapse:collapse;width:100%}
td,th{padding:0.35em 0.6em;text-align:left;border-bottom:1px solid #ccc;vertical-align:top}
aside{display:none}
</style></head><body>`;
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  let files = fs.readdirSync(dir).filter(f => f.endsWith('.html'));
  if (only.length) files = files.filter(f => only.includes(f.replace('.html', '')));
  for (const f of files) {
    const body = fs.readFileSync(path.join(dir, f), 'utf8');
    await page.setContent(head + body + '</body></html>', { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const issues = await page.evaluate(() => {
      const out = [];
      const sec = document.querySelector('section');
      const S = sec.getBoundingClientRect();
      const name = el => (el.id ? '#' + el.id : el.tagName.toLowerCase()) + ' "' + (el.textContent || '').trim().slice(0, 28) + '"';
      const texts = [...sec.querySelectorAll('p,h1,h2,h3,td,th,li')].filter(el => (el.textContent || '').trim() && getComputedStyle(el).opacity !== '0' && !el.closest('[style*="opacity:0"]'));
      const range = document.createRange();
      const inkRect = el => { range.selectNodeContents(el); const rs = [...range.getClientRects()]; if (!rs.length) return null; return { l: Math.min(...rs.map(r => r.left)), t: Math.min(...rs.map(r => r.top)), r: Math.max(...rs.map(r => r.right)), b: Math.max(...rs.map(r => r.bottom)) }; };
      // 1. text overflowing its own box or its container's padding box
      for (const el of texts) {
        const ink = inkRect(el); if (!ink) continue;
        const b = el.getBoundingClientRect();
        if (ink.r > b.right + 1 || ink.b > b.bottom + 6) out.push(`overflow-self ${name(el)} ink r${Math.round(ink.r - b.right)} b${Math.round(ink.b - b.bottom)}`);
        let c = el.parentElement;
        while (c && c !== sec && !(getComputedStyle(c).backgroundColor !== 'rgba(0, 0, 0, 0)' || getComputedStyle(c).borderTopStyle !== 'none')) c = c.parentElement;
        const C = (c || sec).getBoundingClientRect();
        const cs = getComputedStyle(c || sec);
        const pl = parseFloat(cs.paddingLeft), pr = parseFloat(cs.paddingRight), pt = parseFloat(cs.paddingTop), pb = parseFloat(cs.paddingBottom);
        const isSec = !c || c === sec;
        const minGap = isSec ? 40 : 8;
        const gaps = { l: ink.l - C.left, r: C.right - ink.r, t: ink.t - C.top, b: C.bottom - ink.b };
        for (const k of ['l', 'r', 't', 'b']) if (gaps[k] < minGap) out.push(`tight-${k} ${name(el)} in ${isSec ? 'section' : name(c).slice(0, 20)} gap ${Math.round(gaps[k])}`);
      }
      // 2. fixed-height boxes whose content overflows
      for (const d of sec.querySelectorAll('div')) {
        if (d.closest('[style*="opacity:0"]')) continue;
        if (d.scrollHeight > d.clientHeight + 2 && d.style.height) out.push(`box-overflow ${name(d).slice(0, 40)} by ${d.scrollHeight - d.clientHeight}`);
        const r = d.getBoundingClientRect();
        if (r.right > S.right - 40 || r.bottom > S.bottom - 40 || r.left < S.left + 40 || r.top < S.top + 30) out.push(`edge ${name(d).slice(0, 30)} ${Math.round(r.left)},${Math.round(r.top)},${Math.round(r.right)},${Math.round(r.bottom)}`);
      }
      // 3. text overlapping other text
      const inks = texts.map(el => [el, inkRect(el)]).filter(x => x[1]);
      for (let i = 0; i < inks.length; i++) for (let j = i + 1; j < inks.length; j++) {
        const [a, A] = inks[i], [b, B] = inks[j];
        if (a.contains(b) || b.contains(a)) continue;
        const ox = Math.min(A.r, B.r) - Math.max(A.l, B.l), oy = Math.min(A.b, B.b) - Math.max(A.t, B.t);
        if (ox > 2 && oy > 2) out.push(`text-overlap ${name(a)} × ${name(b)}`);
      }
      // 4. text crossing the edge of a painted box it does not belong to
      const boxes = [...sec.querySelectorAll('div,x-shape,x-icon')].filter(d => !d.closest('[style*="opacity:0"]') && (getComputedStyle(d).backgroundColor !== 'rgba(0, 0, 0, 0)' || getComputedStyle(d).borderTopStyle !== 'none' || d.tagName !== 'DIV'));
      for (const [el, T] of inks) for (const d of boxes) {
        if (d.contains(el)) continue;
        const D = d.getBoundingClientRect();
        const ox = Math.min(T.r, D.right) - Math.max(T.l, D.left), oy = Math.min(T.b, D.bottom) - Math.max(T.t, D.top);
        if (ox <= 1 || oy <= 1) continue;
        const inside = T.l >= D.left && T.r <= D.right && T.t >= D.top && T.b <= D.bottom;
        if (!inside) out.push(`cross ${name(el)} × ${name(d).slice(0, 26)}`);
        else if (d.tagName !== 'DIV') out.push(`over-shape ${name(el)} × ${d.tagName}`);
      }
      return out;
    });
    await page.screenshot({ path: path.join(outDir, f.replace('.html', '.png')) });
    console.log(`== ${f}: ${issues.length ? '\n  ' + [...new Set(issues)].join('\n  ') : 'ok'}`);
  }
  await browser.close();
})();
