// Finds text that leaves its box: run before every preview, next to check.js.
// Usage (in a chapter folder): node ../tools/boxcheck.js slides [slide-id ...]
// A box is a div with a background or a border on all four sides. Two problems are reported:
//   OUT       text inside a box whose letters reach past the box edge (minus 4px)
//   STRADDLE  text that is half inside, half outside a box it does not belong to (a tag running over an editor edge)
// Leading spaces of code lines are not counted as letters. Labels with their own background may sit on an edge. Tinted bands (alpha < 0.4) are not boxes.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const [dir, ...only] = process.argv.slice(2);
const src = fs.readFileSync(path.join(__dirname, 'check.js'), 'utf8');
const head = src.match(/const head = `([\s\S]*?)`;/)[1];
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  let files = fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort();
  if (only.length) files = files.filter(f => only.includes(f.replace('.html', '')));
  let total = 0;
  for (const f of files) {
    await page.setContent(head + fs.readFileSync(path.join(dir, f), 'utf8') + '</body></html>', { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const res = await page.evaluate(() => {
      const out = [], sec = document.querySelector('section');
      const ink = el => {
        const rs = [];
        const walk = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        for (let n = walk.nextNode(); n; n = walk.nextNode()) {
          const t = n.textContent, a = t.search(/\S/);
          if (a < 0) continue;
          const b = t.length - (t.length - t.trimEnd().length);
          const r = document.createRange(); r.setStart(n, a); r.setEnd(n, b);
          rs.push(...[...r.getClientRects()].filter(x => x.width > 0));
        }
        if (!rs.length) return null;
        return { l: Math.min(...rs.map(r => r.left)), t: Math.min(...rs.map(r => r.top)), r: Math.max(...rs.map(r => r.right)), b: Math.max(...rs.map(r => r.bottom)) };
      };
      const isBox = d => {
        if (d.tagName !== 'DIV') return false;
        const s = getComputedStyle(d);
        const m = s.backgroundColor.match(/rgba?\(([^)]+)\)/);
        const alpha = m ? (m[1].split(',')[3] === undefined ? 1 : parseFloat(m[1].split(',')[3])) : 0;
        const border = ['Top', 'Right', 'Bottom', 'Left'].every(k => s['border' + k + 'Style'] !== 'none' && parseFloat(s['border' + k + 'Width']) > 0);
        const r = d.getBoundingClientRect();
        return (alpha >= 0.4 || border) && r.width > 60 && r.height > 40;
      };
      const boxes = [...sec.querySelectorAll('div')].filter(isBox);
      const nm = el => (el.id ? '#' + el.id + ' ' : '') + '"' + el.textContent.trim().replace(/\s+/g, ' ').slice(0, 30) + '"';
      for (const p of sec.querySelectorAll('p,h1,h2,h3')) {
        if (!p.textContent.trim()) continue;
        const k = ink(p); if (!k) continue;
        let c = p.parentElement; while (c && c !== sec && !isBox(c)) c = c.parentElement;
        if (c && c !== sec && getComputedStyle(c).overflow !== 'hidden' || (c && c !== sec && c.scrollHeight <= c.clientHeight + 2)) {
          const R = c.getBoundingClientRect();
          if (k.l < R.left + 4 || k.r > R.right - 4 || k.t < R.top - 2 || k.b > R.bottom + 2)
            out.push(`OUT ${nm(p)} in ${nm(c).slice(0, 24)} (l${Math.round(k.l - R.left)} r${Math.round(R.right - k.r)} t${Math.round(k.t - R.top)} b${Math.round(R.bottom - k.b)})`);
        }
        // a label with its own background (a tab on a box border) is meant to sit on the edge
        const pb = getComputedStyle(p).backgroundColor;
        if (pb !== 'rgba(0, 0, 0, 0)' && !/,\s*0\.[0-3]\d*\)$/.test(pb)) continue;
        for (const bx of boxes) {
          if (bx.contains(p) || p.contains(bx)) continue;
          const R = bx.getBoundingClientRect();
          const ix = Math.min(k.r, R.right) - Math.max(k.l, R.left), iy = Math.min(k.b, R.bottom) - Math.max(k.t, R.top);
          if (ix <= 2 || iy <= 2) continue;
          const inside = k.l >= R.left - 1 && k.r <= R.right + 1 && k.t >= R.top - 1 && k.b <= R.bottom + 1;
          if (!inside) out.push(`STRADDLE ${nm(p)} over the edge of ${nm(bx).slice(0, 24)}`);
        }
      }
      return out;
    });
    if (res.length) { console.log('== ' + f); res.forEach(r => console.log('  ' + r)); total += res.length; }
  }
  console.log(total ? `${total} problems in ${files.length} slides` : `no text leaves its box (${files.length} slides)`);
  await browser.close();
})();
