// 릴리스 노트에 넣을 그림을 실제 덱(41)으로 만들어요.
// 사용법 (레포 맨 위에서): node updates/2026-11-28-copyright/tools/shots.js
// 1) 표지 맨 아래 한 줄 2) 슬라이드 오른쪽 아래 작은 줄 3) PDF 쪽 아래 띠 (pdftoppm, ImageMagick 필요)
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const path = require('path');

const ROOT = path.resolve(__dirname, '../../..');
const OUT = path.resolve(__dirname, '../img');
const DECK = '41-sql-subquery/sql-subquery-slides';

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  await page.goto('file://' + path.join(ROOT, DECK + '.html'));
  await page.evaluate(() => localStorage.setItem('slides-anim', 'off'));
  for (const [n, file, clip] of [[1, '01-cover.png', { x: 0, y: 560, width: 1920, height: 520 }], [4, '02-corner.png', { x: 960, y: 640, width: 960, height: 440 }]]) {
    await page.goto('file://' + path.join(ROOT, DECK + '.html') + '#' + n);
    await page.reload();
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(1200);
    await page.screenshot({ path: path.join(OUT, file), clip });
  }
  await browser.close();
  const tmp = path.join(OUT, 'tmp-page');
  execFileSync('pdftoppm', ['-f', '4', '-l', '4', '-r', '96', '-png', '-singlefile', path.join(ROOT, DECK + '.pdf'), tmp]);
  execFileSync('convert', [tmp + '.png', '-crop', '1920x324+0+800', '+repage', path.join(OUT, '03-pdf-strip.png')]);
  execFileSync('rm', [tmp + '.png']);
  console.log('shots -> ' + OUT);
})();
