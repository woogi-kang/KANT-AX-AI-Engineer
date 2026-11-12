// Screenshots every slide of a built player HTML after all its animations have played, for the full-size review.
// Usage (in a chapter folder): node ../tools/playshots.js 주제-slides.html shots-play
// Each slide is opened by number, then advanced step by step to its last build and given time to settle,
// so pen boxes, morphs, text changes and pans are seen in their end state, the way the instructor will show them.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const [file, outDir] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.resolve(file));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1000);
  const n = await page.evaluate(() => document.querySelectorAll('section').length);
  // read the player's own counter: slide text such as [1/4] or (9/9) must not be taken for the page number
  const pageNo = async () => page.evaluate(() => +((document.getElementById('pl-count') || document.body).textContent.match(/(\d+)\s*\/\s*\d+/) || [])[1]);
  for (let i = 1; i <= n; i++) {
    await page.keyboard.type(String(i)); await page.keyboard.press('Enter'); await page.waitForTimeout(400);
    for (let k = 0; k < 30; k++) {           // play every build on this slide, stop before the next slide
      await page.keyboard.press('ArrowRight'); await page.waitForTimeout(700);
      if (await pageNo() !== i) { await page.keyboard.press('ArrowLeft'); await page.waitForTimeout(400); break; }
    }
    await page.waitForTimeout(2500);
    await page.screenshot({ path: path.join(outDir, String(i).padStart(2, '0') + '.png') });
  }
  console.log(`${n} slides -> ${outDir}`);
  await browser.close();
})();
