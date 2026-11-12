// Takes the Docker Hub screenshots the deck uses (real pages, 1600x1000 viewport).
// Usage (in 29-docker-basics): node tools/hubshots.js tools/src
const { chromium } = require('playwright');
const out = process.argv[2] || 'tools/src';
const pages = [
  ['hub-search', 'https://hub.docker.com/search?q=nginx'],
  ['hub-nginx', 'https://hub.docker.com/_/nginx'],
  ['hub-python-tags', 'https://hub.docker.com/_/python/tags?name=3.12-slim'],
];
(async () => {
  const b = await chromium.launch({ proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined });
  const ctx = await b.newContext({ viewport: { width: 1600, height: 1000 }, locale: 'en-US', ignoreHTTPSErrors: true });
  for (const [name, url] of pages) {
    const p = await ctx.newPage();
    await p.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(e => console.log('goto', e.message));
    await p.waitForTimeout(3000);
    for (const t of ['Accept All Cookies', 'Accept all', 'Reject All']) {
      const btn = p.getByRole('button', { name: t });
      if (await btn.count()) { await btn.first().click().catch(() => {}); break; }
    }
    // logos come from a host this machine cannot reach; hide the broken-image boxes
    await p.addStyleTag({ content: 'img{visibility:hidden !important}' });
    await p.waitForTimeout(1000);
    await p.screenshot({ path: `${out}/${name}.png` });
    console.log(name, await p.title());
    await p.close();
  }
  await b.close();
})();
