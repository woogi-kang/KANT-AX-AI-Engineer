// 릴리스 노트에 넣을 스크린샷을 실제 덱(13)으로 찍어요.
// 사용법 (레포 맨 위에서): node updates/2026-11-09-notes-window/tools/shots.js
const { chromium } = require('playwright');
const path = require('path');

const ROOT = path.resolve(__dirname, '../../..');
const OUT = path.resolve(__dirname, '../img');
const DECK = 'file://' + path.join(ROOT, '13-python-strings-lists/python-strings-lists-slides.html');
const W = 1600, H = 900;
const RED = '#E5484D', BLUE = '#2459C9';

// 화면 위에 강조 상자와 설명 말풍선을 덧그려요. 좌표는 화면(px) 기준이에요.
async function annotate(page, marks) {
  await page.evaluate(({ marks, RED }) => {
    document.querySelectorAll('.anno').forEach(e => e.remove());
    for (const m of marks) {
      if (m.box) {
        const d = document.createElement('div');
        d.className = 'anno';
        Object.assign(d.style, {
          position: 'fixed', left: m.box.x + 'px', top: m.box.y + 'px', width: m.box.w + 'px', height: m.box.h + 'px',
          border: `4px ${m.dashed ? 'dashed' : 'solid'} ${m.color || RED}`, borderRadius: '12px', zIndex: 9998,
          pointerEvents: 'none', boxSizing: 'border-box', background: m.fill || 'transparent',
        });
        document.body.appendChild(d);
      }
      if (m.label) {
        const t = document.createElement('div');
        t.className = 'anno';
        t.innerHTML = m.label;
        Object.assign(t.style, {
          position: 'fixed', maxWidth: (m.width || 420) + 'px',
          padding: '12px 18px', borderRadius: '12px', background: m.color || RED, color: '#fff',
          font: "700 22px/1.4 'Noto Sans KR', Arial, sans-serif", zIndex: 9999, pointerEvents: 'none',
          boxShadow: '0 4px 14px rgba(0,0,0,.25)', whiteSpace: m.nowrap ? 'nowrap' : 'normal',
          transform: m.anchor || 'none',
        });
        for (const k of ['left', 'top', 'right', 'bottom']) {
          const v = m.at[k] ?? m.at[{ left: 'x', top: 'y' }[k]];
          if (v !== undefined) t.style[k] = v + 'px';
        }
        document.body.appendChild(t);
      }
    }
  }, { marks, RED });
}
const box = page => page.$eval('#pl-notes', e => { const r = e.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; });
async function drag(page, from, to) {
  await page.mouse.move(from.x, from.y); await page.mouse.down();
  await page.mouse.move(to.x, to.y, { steps: 10 }); await page.mouse.up();
}

(async () => {
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 2 })).newPage();
  await page.goto(DECK + '#8');
  await page.waitForTimeout(600);
  await page.keyboard.press('a'); await page.waitForTimeout(300);
  await page.keyboard.press('n'); await page.waitForTimeout(2200);

  // 1. 처음 자리: 위쪽 띠와 모서리를 표시해요
  let b = await box(page);
  const nh = await page.$eval('#pl-notes .nh', e => e.getBoundingClientRect().height);
  await annotate(page, [
    { box: { x: b.x - 6, y: b.y - 6, w: b.w + 12, h: nh + 12 }, label: '위쪽을 잡고 끌면 옮겨져요', at: { x: b.x, y: b.y - 70 }, nowrap: true },
    { box: { x: b.x + b.w - 34, y: b.y + b.h - 34, w: 40, h: 40 }, label: '모서리나 가장자리를 끌면 크기가 바뀌어요', at: { x: b.x - 600, y: b.y + b.h - 110 }, color: BLUE, nowrap: true },
  ]);
  await page.screenshot({ path: path.join(OUT, '01-grab.png') });
  await annotate(page, []);

  // 2. 왼쪽 아래로 옮기고 작게 줄여요
  await drag(page, { x: b.x + 160, y: b.y + 30 }, { x: 160 + 30, y: H - 380 });
  b = await box(page);
  await drag(page, { x: b.x + b.w - 8, y: b.y + b.h - 8 }, { x: b.x + 360, y: b.y + 300 });
  b = await box(page);
  await annotate(page, [{ box: { x: b.x - 6, y: b.y - 6, w: b.w + 12, h: b.h + 12 }, label: '작게 줄여서 왼쪽 아래로', at: { x: b.x + b.w + 24, y: b.y + 10 }, nowrap: true }]);
  await page.screenshot({ path: path.join(OUT, '02-small.png') });
  await annotate(page, []);

  // 3. 크게 늘려요
  await drag(page, { x: b.x + 160, y: b.y + 30 }, { x: 1180, y: 40 });
  b = await box(page);
  await drag(page, { x: b.x + 3, y: b.y + b.h / 2 }, { x: 900, y: b.y + b.h / 2 });
  b = await box(page);
  await drag(page, { x: b.x + b.w - 3, y: b.y + b.h / 2 }, { x: W - 110, y: b.y + b.h / 2 });
  b = await box(page);
  await drag(page, { x: b.x + b.w / 2, y: b.y + b.h - 3 }, { x: b.x + b.w / 2, y: H - 100 });
  b = await box(page);
  await annotate(page, [{ box: { x: b.x - 6, y: b.y - 6, w: b.w + 12, h: b.h + 12 }, label: '크게 늘려서 오른쪽에', at: { x: b.x - 330, y: b.y + 120 }, nowrap: true }]);
  await page.screenshot({ path: path.join(OUT, '03-large.png') });
  await annotate(page, []);

  // 4. 새로 고침해도 같은 자리에 있어요
  await page.reload(); await page.waitForTimeout(600);
  await page.keyboard.press('n'); await page.waitForTimeout(2200);
  const after = await box(page);
  console.log('reload keeps box:', Math.round(after.x) === Math.round(b.x) && Math.round(after.w) === Math.round(b.w));
  await browser.close();
})();
