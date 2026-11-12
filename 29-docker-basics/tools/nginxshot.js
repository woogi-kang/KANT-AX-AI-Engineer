// Screenshot of the nginx welcome page served by: docker run -d --name web -p 8080:80 nginx
// Usage (in 29-docker-basics, with that container running): node tools/nginxshot.js tools/src/nginx-welcome.png
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1100, height: 560 } });
  await p.goto('http://localhost:8080');
  await p.screenshot({ path: process.argv[2] });
  await b.close();
})();
