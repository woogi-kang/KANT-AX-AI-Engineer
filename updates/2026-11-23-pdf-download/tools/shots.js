// 릴리스 노트에 넣을 그림을 실제 덱(45)으로 만들어요.
// 사용법 (레포 맨 위에서): node updates/2026-11-23-pdf-download/tools/shots.js
// 1) 아래 막대의 PDF 받기 버튼 2) 그 버튼으로 받은 PDF의 한 쪽 (pdftoppm 필요)
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const path = require('path');

const ROOT = path.resolve(__dirname, '../../..');
const OUT = path.resolve(__dirname, '../img');
const DECK = '45-numpy-pandas/numpy-pandas-slides';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.join(ROOT, DECK + '.html') + '#12');
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);
  await page.mouse.move(960, 900);
  await page.hover('#pl-pdf');
  await page.waitForTimeout(400);
  const b = await page.$eval('#pl-bar', e => { const r = e.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; });
  await page.screenshot({ path: path.join(OUT, '01-button.png'), clip: { x: b.x - 60, y: b.y - 80, width: b.w + 120, height: b.h + 96 } });
  await browser.close();
  execFileSync('pdftoppm', ['-f', '12', '-l', '12', '-scale-to-x', '1600', '-scale-to-y', '-1', '-png', '-singlefile',
    path.join(ROOT, DECK + '.pdf'), path.join(OUT, '02-pdf-page')]);
  console.log('shots -> ' + OUT);
})();
