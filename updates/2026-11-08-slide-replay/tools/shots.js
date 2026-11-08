// 릴리스 노트에 넣을 스크린샷을 실제 덱(13)으로 찍어요.
// 사용법 (레포 맨 위에서): node updates/2026-11-08-slide-replay/tools/shots.js
// 전후 비교를 넣으려면 BEFORE_HTML(13 덱), BEFORE_NOTES_HTML(24 덱)에 예전 플레이어로 만든 HTML 경로를 같이 줘요.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '../../..');
const OUT = path.resolve(__dirname, '../img');
const PY = 'file://' + path.join(ROOT, '13-python-strings-lists/python-strings-lists-slides.html');
const CLS = 'file://' + path.join(ROOT, '24-python-class/python-class-slides.html');
const W = 1600, H = 900;
const RED = '#E5484D';

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
const rect = (page, sel) => page.evaluate(s => {
  const el = typeof s === 'string' ? document.querySelector(s) : null;
  const r = el.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height };
}, sel);
const pad = (r, p) => ({ x: r.x - p, y: r.y - p, w: r.w + 2 * p, h: r.h + 2 * p });
async function open(page, url, n) {
  await page.goto('about:blank');
  await page.goto(url + '#' + n);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(600);
}
async function buildAll(page) {
  // 지금 장의 애니메이션을 끝까지 펼쳐요 (Space를 누르다 장이 바뀌기 직전에 멈춰요)
  const start = await page.evaluate(() => location.hash);
  for (let i = 0; i < 20; i++) {
    const left = await page.evaluate(() => document.querySelectorAll('#pl-stage>section.on .pending').length);
    if (!left) break;
    await page.keyboard.press('Space');
    await page.waitForTimeout(150);
  }
  if (await page.evaluate(() => location.hash) !== start) throw new Error('slide moved');
  await page.waitForTimeout(600);
}
async function codeBox(page) {
  return page.evaluate(() => {
    const r = document.querySelector('#pl-stage>section.on [data-code]').getBoundingClientRect();
    return { x: r.left, y: r.top, w: r.width, h: r.height };
  });
}
const shot = (page, name) => page.screenshot({ path: path.join(OUT, name) });
// 스크린샷 두 장을 제목과 함께 나란히 붙여요
let ctxRef;
async function sideBySide(name, panels) {
  const cmp = await ctxRef.newPage();
  await cmp.setViewportSize({ width: 1600, height: 100 });
  const img = b => 'data:image/png;base64,' + b.toString('base64');
  await cmp.setContent(`<html><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@500;700&display=swap"></head>
  <body style="margin:0;background:#F6F5F1;font-family:'Noto Sans KR'">
  <div style="display:flex;gap:56px;padding:36px 40px;align-items:flex-start;position:relative">
  ${panels.map(([b, t, sub, c], i) => `
  <div style="flex:1;display:flex;flex-direction:column;gap:14px">
    <div style="font-size:28px;font-weight:700;color:${c}">${t} <span style="font-weight:500;color:#1D2330">· ${sub}</span></div>
    <img src="${img(b)}" style="width:100%;border-radius:12px;border:4px solid ${c};box-sizing:border-box">
  </div>${i < panels.length - 1 ? '<div style="align-self:center;font-size:44px;color:#1D2330;margin:40px -40px 0">&#8594;</div>' : ''}`).join('')}
  </div></body></html>`);
  await cmp.evaluate(() => document.fonts.ready); await cmp.waitForTimeout(400);
  await cmp.screenshot({ path: path.join(OUT, name), fullPage: true });
  await cmp.close();
}
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: W, height: H } });
  ctxRef = ctx;
  const page = await ctx.newPage();
  const pending = () => page.evaluate(() => document.querySelectorAll('#pl-stage>section.on .pending').length);

  // 1. 다 본 장에서 R을 누르면 처음 화면으로 돌아가고, → 로 하나씩 다시 나와요
  await open(page, PY, 20); await buildAll(page);
  await page.keyboard.press('ArrowRight'); await page.waitForTimeout(500);
  await page.keyboard.press('ArrowLeft'); await page.waitForTimeout(900);
  if (await pending()) throw new Error('not finished on return');
  const top = { clip: { x: 0, y: 0, width: W, height: 620 } }; // 위쪽만 잘라서 크게 보여 줘요
  const done = await page.screenshot(top);
  await page.keyboard.press('r'); await page.waitForTimeout(600);
  if (!(await pending())) throw new Error('R did not reset');
  const toastR = await rect(page, '#pl-toast');
  await annotate(page, [{ box: pad(toastR, 8) }]);
  const reset = await page.screenshot(top);
  await annotate(page, []);
  await page.keyboard.press('ArrowRight'); await page.waitForTimeout(400);
  await page.keyboard.press('ArrowRight'); await page.waitForTimeout(900);
  const again = await page.screenshot(top);
  await sideBySide('01-replay.png', [
    [done, '다 본 장', '완성된 화면이에요', '#6A7180'],
    [reset, 'R을 누르면', '처음 화면으로 돌아가요', RED],
    [again, '→ 를 누르면', '하나씩 다시 나와요', '#1F8A4C'],
  ]);

  // 2. 간단해진 아래 막대: 전과 후를 위아래로 붙여요 (전 화면은 main에 있던 플레이어로 찍어요)
  await open(page, PY, 22); await buildAll(page);
  await page.addStyleTag({ content: '#pl-stage>section{opacity:0!important}' }); // 막대만 보이게 슬라이드 글자를 숨겨요
  await page.mouse.move(W / 2, H / 2); await page.waitForTimeout(400);
  const barAfter = await page.screenshot({ clip: { x: W / 2 - 320, y: H - 90, width: 640, height: 90 } });
  await page.hover('#pl-replay'); await page.waitForTimeout(400);
  const tip = await page.screenshot({ clip: { x: W / 2 - 320, y: H - 130, width: 640, height: 130 } });
  const BEFORE = process.env.BEFORE_HTML;
  const panels = [];
  if (BEFORE) {
    await open(page, 'file://' + BEFORE, 22);
    await page.addStyleTag({ content: '#pl-stage>section{opacity:0!important}' }); // 막대만 보이게 슬라이드 글자를 숨겨요
    await page.mouse.move(W / 2, H / 2); await page.waitForTimeout(400);
    panels.push(['<b style="color:#6A7180">전</b> · 버튼과 키 설명이 한 줄에 다 있었어요', await page.screenshot({ clip: { x: 0, y: H - 60, width: W, height: 60 } })]);
  }
  panels.push(['<b style="color:#E5484D">후</b> · 아이콘만 남긴 작은 막대예요', barAfter]);
  panels.push(['<b style="color:#1F8A4C">아이콘에 마우스를 올리면</b> · 이름과 단축키가 보여요', tip]);
  const cmp = await ctx.newPage();
  await cmp.setViewportSize({ width: W, height: 100 });
  await cmp.setContent(`<html><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@500;700&display=swap"></head>
  <body style="margin:0;background:#F6F5F1;font-family:'Noto Sans KR';color:#1D2330;padding:28px 40px">
  ${panels.map(([t, b]) => `<div style="font-size:26px;font-weight:500;margin:18px 0 10px">${t}</div><img src="data:image/png;base64,${b.toString('base64')}" style="display:block;max-width:100%;border-radius:10px;border:2px solid #E1DED6;box-sizing:border-box">`).join('')}
  </body></html>`);
  await cmp.evaluate(() => document.fonts.ready); await cmp.waitForTimeout(400);
  await cmp.screenshot({ path: path.join(OUT, '02-bar.png'), fullPage: true });
  await cmp.close();

  // 3. ? 버튼을 누르면 단축키 안내
  await page.goto('about:blank');
  await open(page, PY, 22); await buildAll(page);
  await page.click('#pl-help-btn'); await page.mouse.move(W / 2, H / 2); await page.waitForTimeout(400);
  const hb = await rect(page, '#pl-help-btn');
  await annotate(page, [{ box: pad(hb, 4) }]);
  await shot(page, '03-help.png');
  await page.keyboard.press('Escape');

  // 4. 애니메이션이 꺼져 있을 때
  await page.evaluate(() => document.querySelectorAll('.anno').forEach(e => e.remove()));
  await page.keyboard.press('a'); await page.waitForTimeout(2200);
  await page.keyboard.press('r'); await page.waitForTimeout(500);
  const toastOff = await rect(page, '#pl-toast');
  await annotate(page, [{ box: pad(toastOff, 8) }]);
  await shot(page, '04-animation-off.png');
  await page.keyboard.press('a');

  // 5. 발표자 노트: 전과 후를 나란히 (전 화면은 BEFORE_NOTES_HTML, 예전 플레이어로 만든 24 덱)
  const noteShot = async (url) => {
    await page.goto('about:blank');
    await open(page, url, 12); await page.keyboard.press('ArrowRight');
    await page.keyboard.press('n'); await page.mouse.move(W * 0.4, H / 2); await page.waitForTimeout(500);
    return page.screenshot();
  };
  const afterNote = await noteShot(CLS);
  if (process.env.BEFORE_NOTES_HTML) {
    const beforeNote = await noteShot('file://' + process.env.BEFORE_NOTES_HTML);
    await sideBySide('05-notes.png', [
      [beforeNote, '전', '긴 글이 한 덩어리로 나왔어요', '#6A7180'],
      [afterNote, '후', '요점, 한 줄씩, 코드 이름이 구분돼요', RED],
    ]);
  } else await shot(page, '05-notes.png');
  await browser.close();
  console.log('shots ->', OUT);
})();
