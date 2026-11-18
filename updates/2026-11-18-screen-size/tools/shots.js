// Screenshots for this release note, taken from the real decks at several window sizes.
// Usage (repo root): node updates/2026-11-18-screen-size/tools/shots.js
const { chromium } = require('playwright');
const path = require('path');
const root = path.resolve(__dirname, '../../..');
const img = n => path.join(__dirname, '..', 'img', n);
const deck = root + '/36-sql-basics/sql-basics-slides.html';
async function open(b, w, h, opts = {}) {
  const c = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: opts.dpr || 1, isMobile: !!opts.mobile, hasTouch: !!opts.mobile });
  if (!opts.tip) await c.addInitScript(() => { try { sessionStorage.setItem('slides-fs-tip', '1'); } catch (e) {} });
  const p = await c.newPage();
  await p.goto('file://' + deck + '#' + (opts.slide || 15));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(1000);
  return p;
}
(async () => {
  const b = await chromium.launch();
  // 1. mouse moving: arrows and bar show; 2. mouse still for 2 seconds: they are gone
  let p = await open(b, 1280, 720);
  await p.mouse.move(640, 300); await p.mouse.move(650, 300); await p.waitForTimeout(400);
  await p.screenshot({ path: img('01-moving.png') });
  await p.waitForTimeout(2600);
  await p.screenshot({ path: img('02-still.png') });
  // 3. a wide browser window: light bands on both sides, arrows inside the bands
  p = await open(b, 1920, 960);
  await p.mouse.move(960, 300); await p.mouse.move(970, 300); await p.waitForTimeout(400);
  await p.screenshot({ path: img('03-bands.png') });
  // 4. a small window: the full-screen tip
  p = await open(b, 1024, 640, { tip: true });
  await p.waitForTimeout(700);
  await p.screenshot({ path: img('04-small.png') });
  // 5. a phone held upright
  p = await open(b, 390, 844, { dpr: 2, mobile: true });
  await p.screenshot({ path: img('05-phone.png') });
  await b.close();
  console.log('5 shots -> updates/2026-11-18-screen-size/img');
})();
