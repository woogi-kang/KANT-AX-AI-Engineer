// Saves where every element with an id is drawn on each slide, so gen.py can aim leader lines at real boxes.
// gen.py runs it between its two passes. Usage: node tools/measure.js slides tools/rects.json
const fs = require('fs');
const path = require('path');
const { renderDeck } = require(path.join(__dirname, '..', '..', 'tools', 'deckrender'));
const [dir, out] = process.argv.slice(2);
(async () => {
  const { browser, page } = await renderDeck(dir);
  const rects = await page.evaluate(() => {
    const all = {};
    for (const s of document.querySelectorAll('body > section')) {
      const S = s.getBoundingClientRect(), m = {};
      for (const el of s.querySelectorAll('[id]')) {
        const b = el.getBoundingClientRect();
        m[el.id] = [b.left - S.left, b.top - S.top, b.width, b.height].map(v => Math.round(v));
      }
      all[s.id] = m;
    }
    return all;
  });
  await browser.close();
  fs.writeFileSync(out, JSON.stringify(rects));
})();
