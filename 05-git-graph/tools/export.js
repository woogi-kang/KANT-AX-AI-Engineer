// Exports every slide in deck.json order to a single PDF (one 1920x1080 page per slide).
// Usage: node tools/export.js slides git-basics-slides.pdf
const { renderDeck } = require('./deckrender');
const [dir, out] = process.argv.slice(2);

(async () => {
  const { deck, browser, page } = await renderDeck(dir, '@page{size:1920px 1080px;margin:0} section{break-after:page}');
  await page.pdf({ path: out, width: '1920px', height: '1080px', printBackground: true });
  await browser.close();
  console.log(`${deck.order.length} slides -> ${out}`);
})();
