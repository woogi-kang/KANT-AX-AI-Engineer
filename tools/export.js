// Exports every slide in deck.json order to a single PDF (one page per slide).
// Each page is the 1920x1080 slide with a 44px strip under it: the copyright line on the left,
// the page number on the right, so the strip never covers the slide.
// Usage: node tools/export.js slides git-basics-slides.pdf
const { renderDeck, PDF_LINE } = require('./deckrender');
const [dir, out] = process.argv.slice(2);
const STRIP = 44;
const CSS = `@page{size:1920px ${1080 + STRIP}px;margin:0}
.pdf-strip{width:1920px;height:${STRIP}px;box-sizing:border-box;padding:0 40px;display:flex;align-items:center;justify-content:space-between;background:#E9E7E1;color:#6B7280;font:400 16px/1 'Noto Sans KR',Arial,sans-serif;break-after:page;-webkit-print-color-adjust:exact;print-color-adjust:exact}`;

(async () => {
  const { deck, browser, page } = await renderDeck(dir, CSS);
  await page.evaluate(line => {
    const secs = [...document.querySelectorAll('body > section')];
    secs.forEach((s, i) => {
      const strip = document.createElement('div');
      strip.className = 'pdf-strip';
      strip.innerHTML = '<span></span><span></span>';
      strip.children[0].textContent = line;
      strip.children[1].textContent = (i + 1) + ' / ' + secs.length;
      s.after(strip);
    });
  }, PDF_LINE);
  await page.pdf({ path: out, width: '1920px', height: `${1080 + STRIP}px`, printBackground: true });
  await browser.close();
  console.log(`${deck.order.length} slides -> ${out}`);
})();
