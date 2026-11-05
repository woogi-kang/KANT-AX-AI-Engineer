// 릴리스 노트에 넣을 스크린샷을 실제 덱(24, 25, 26)의 눌러 보기 장에서 찍어요.
// 사용법 (레포 맨 위에서): node updates/2026-11-05-class-labs/tools/shots.js
const { chromium } = require('playwright');
const path = require('path');

const ROOT = path.resolve(__dirname, '../../..');
const OUT = path.resolve(__dirname, '../img');
const deck = (dir, file) => 'file://' + path.join(ROOT, dir, file);
// [파일 이름, 덱, 쪽, 차례로 누를 버튼, 마지막으로 기다릴 시간(ms)]
const SHOTS = [
  ['01-stamp.png', deck('24-python-class', 'python-class-slides.html'), 17, ['#lb-flavors >> text=슈크림', '#lb-next', '#lb-next', '#lb-next'], 900],
  ['02-who.png', deck('25-python-str-repr', 'python-str-repr-slides.html'), 14, ['text=__str__ 있음', 'button[data-k=fstr]'], 3000],
  ['03-find.png', deck('26-python-inheritance', 'python-inheritance-slides.html'), 17, ['#lf-go'], 3800],
];

(async () => {
  const browser = await chromium.launch();
  for (const [name, url, n, clicks, wait] of SHOTS) {
    const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
    await page.goto(url + '#' + n);
    await page.waitForTimeout(800);
    await page.keyboard.press('a');   // 애니메이션을 꺼서 장의 설명을 다 펼쳐요
    await page.waitForTimeout(2200);  // 위에 뜬 안내 글이 사라질 때까지
    for (const c of clicks) { await page.click(c); await page.waitForTimeout(700); }
    await page.waitForTimeout(wait);
    await page.addStyleTag({ content: '#pl-bar,.hint{display:none!important}' });   // 아래 막대와 화살표는 빼고 찍어요
    await page.screenshot({ path: path.join(OUT, name) });
    await page.close();
  }
  await browser.close();
  console.log('saved to', OUT);
})();
