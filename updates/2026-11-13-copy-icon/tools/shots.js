// 릴리스 노트에 넣을 스크린샷을 실제 덱(02, 12)으로 찍어요.
// 사용법 (레포 맨 위에서): node updates/2026-11-13-copy-icon/tools/shots.js
const { chromium } = require('playwright');
const path = require('path');

const ROOT = path.resolve(__dirname, '../../..');
const OUT = path.resolve(__dirname, '../img');

// 덱을 열고 n쪽으로 가서 i번째 코드 칸에 마우스를 올린 뒤, 버튼 둘레를 잘라 찍어요.
async function shot(ctx, deck, n, i, file, opts = {}) {
  const page = await ctx.newPage();
  await page.goto('file://' + path.join(ROOT, deck) + '#' + n);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);
  const r = await page.evaluate(([n, i]) => {
    const el = document.querySelectorAll('section')[n - 1].querySelectorAll('[data-code]')[i];
    const q = el.getBoundingClientRect(); return { x: q.left, y: q.top, w: q.width, h: q.height };
  }, [n, i]);
  await page.mouse.move(r.x + 40, r.y + r.h / 2);
  await page.waitForTimeout(200);
  const b = await page.evaluate(() => { const q = document.getElementById('pl-copy').getBoundingClientRect(); return { x: q.left, y: q.top }; });
  if (!opts.stay) await page.mouse.move(b.x + 17, b.y + 17, { steps: 10 });
  if (opts.click) await page.mouse.click(b.x + 17, b.y + 17);
  await page.waitForTimeout(300);
  const clip = opts.clip(r, b);
  await page.screenshot({ path: path.join(OUT, file), clip });
  await page.close();
}

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2, permissions: ['clipboard-read', 'clipboard-write'] });
  await ctx.addInitScript(() => { try { localStorage.setItem('slides-anim', 'off'); } catch (e) {} });
  const wide = (r, b) => ({ x: Math.max(0, b.x - 900), y: Math.max(0, r.y - 30), width: 1000, height: Math.min(r.h + 60, 420) });
  await shot(ctx, '02-git-basics/git-basics-slides.html', 10, 0, '01-icon.png', { clip: wide });
  await shot(ctx, '02-git-basics/git-basics-slides.html', 10, 0, '02-done.png', { click: true, clip: wide });
  await shot(ctx, '12-python-basics/python-basics-slides.html', 3, 0, '03-outside.png', { stay: true, clip: (r, b) => ({ x: Math.max(0, r.x - 120), y: r.y - 40, width: b.x + 120 - (r.x - 120), height: r.h + 140 }) });
  await browser.close();
  console.log('shots -> ' + OUT);
})();
