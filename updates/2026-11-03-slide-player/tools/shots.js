// 릴리스 노트에 넣을 스크린샷을 실제 덱(02, 13)으로 찍어요.
// 사용법 (레포 맨 위에서): node updates/2026-11-03-slide-player/tools/shots.js
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '../../..');
const OUT = path.resolve(__dirname, '../img');
const GIT = 'file://' + path.join(ROOT, '02-git-basics/git-basics-slides.html');
const PY = 'file://' + path.join(ROOT, '13-python-strings-lists/python-strings-lists-slides.html');
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
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, permissions: ['clipboard-read', 'clipboard-write'] });
  ctxRef = ctx;
  const page = await ctx.newPage();

  // 1. 좌우 끝을 눌러야 넘어가요
  await open(page, GIT, 4); await buildAll(page);
  await page.mouse.move(W - 40, H / 2);
  // 화살표는 마우스가 있는 쪽만 나타나요. 안내 그림에서는 양쪽을 같이 보여 줘요
  await page.evaluate(() => document.body.classList.add('edge-l', 'edge-r'));
  await page.waitForTimeout(400);
  const edge = W * 0.15;
  await annotate(page, [
    { box: { x: 4, y: 4, w: edge - 8, h: H - 8 }, dashed: true },
    { box: { x: W - edge + 4, y: 4, w: edge - 8, h: H - 8 }, dashed: true },
    { label: '여기를 클릭하면<br>이전 장', at: { x: 22, y: 60 }, width: edge - 40 },
    { label: '여기를 클릭하면<br>다음 장', at: { x: W - edge + 18, y: 60 }, width: edge - 40 },
    { label: '가운데는 클릭해도 넘어가지 않아요', at: { x: W / 2, y: H - 120 }, anchor: 'translateX(-50%)', color: '#1D2330', nowrap: true },
  ]);
  await shot(page, '01-edge-click.png');

  // 2. 글자를 드래그해서 선택해도 넘어가지 않아요
  await open(page, PY, 19); await buildAll(page);
  const para = await page.evaluate(() => {
    const p = [...document.querySelectorAll('#pl-stage>section.on p')].find(p => p.textContent.startsWith('변수 하나에'));
    const r = p.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height };
  });
  // 드래그 선택은 끝에서 시작해도 넘어가지 않아요. 끝을 그냥 누르는 것만 넘겨요
  const x1 = para.x + 2, x2 = para.x + para.w - 2, y = para.y + para.h / 2;
  const drag = async () => { await page.mouse.move(x1, y); await page.mouse.down(); await page.mouse.move(x2, y, { steps: 8 }); await page.mouse.up(); };
  const before = await page.evaluate(() => location.hash);
  await drag();
  await page.mouse.click(W / 2, H * 0.7); // 선택한 뒤 가운데를 눌러도
  await drag();
  await page.mouse.move(W / 2, H * 0.45); // 끝 화살표가 보이지 않게 마우스를 가운데로
  if (await page.evaluate(() => location.hash) !== before) throw new Error('selection turned the page');
  await page.waitForTimeout(300);
  const sel = await page.evaluate(() => { const r = getSelection().getRangeAt(0).getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; });
  await annotate(page, [
    { box: pad(sel, 10) },
    { label: '드래그해서 선택해도 장이 넘어가지 않아요. 선택한 뒤 Ctrl+C(Mac은 command+C)로 복사해요', at: { x: sel.x, bottom: H - sel.y + 24 }, width: 600 },
  ]);
  await shot(page, '02-select-text.png');

  // 3, 4. 복사 버튼: 마우스를 올린 화면과 누른 뒤 화면을 나란히 붙여요
  async function copyShot(url, n, name, area, noteAt, labels) {
    await open(page, url, n); await buildAll(page);
    const box = await codeBox(page);
    await page.mouse.move(box.x + box.w / 2, box.y + box.h / 2);
    await page.waitForTimeout(300);
    let btn = await rect(page, '#pl-copy');
    const label = await page.evaluate(() => document.getElementById('pl-copy').textContent);
    await annotate(page, [{ box: pad(btn, 6) }]);
    const clip = { x: area.x, y: area.y, width: area.w, height: area.h };
    const hover = await page.screenshot({ clip });
    await page.click('#pl-copy');
    await page.waitForTimeout(300);
    const text = await page.evaluate(() => navigator.clipboard.readText());
    btn = await rect(page, '#pl-copy');
    await annotate(page, [
      { box: pad(btn, 6), color: '#1F8A4C' },
      { label: '복사된 내용<pre style="margin:8px 0 0;font:500 20px/1.5 \'JetBrains Mono\',monospace;white-space:pre">' + esc(text) + '</pre>', at: noteAt(box, btn), width: 520, color: '#1F8A4C' },
    ]);
    const done = await page.screenshot({ clip });
    await sideBySide(name, [
      [hover, '1. 마우스를 올리면', `오른쪽 위에 "${label}" 버튼이 나타나요`, RED],
      [done, '2. 버튼을 누르면', labels, '#1F8A4C'],
    ]);
  }
  await copyShot(GIT, 12, '03-copy-terminal.png', { x: 60, y: 545, w: 1000, h: 308 },
    (box, btn) => ({ right: W - (box.x + box.w) + 24, top: btn.y + btn.h + 24 }), '$ 뒤 명령만 복사돼요');
  await copyShot(PY, 19, '04-copy-python.png', { x: 60, y: 150, w: 720, h: 490 },
    (box) => ({ x: box.x + 10, y: box.y + box.h + 130 }), '코드 전체가 복사돼요');

  // 5. 뒤로 가면 다 펼쳐진 화면 (두 장을 찍어서 나란히 붙여요)
  await open(page, PY, 20);
  await page.mouse.move(W / 2, H / 2);
  await page.keyboard.press('ArrowRight'); // 3쪽에서 4쪽으로 처음 넘어온 화면
  await page.waitForTimeout(900);
  if (await page.evaluate(() => location.hash) !== '#21') { await buildAll(page); await page.keyboard.press('ArrowRight'); await page.waitForTimeout(900); }
  const fwd = await page.screenshot();
  await page.keyboard.press('ArrowRight'); // 4쪽을 펼치는 중이면 한 칸씩
  for (let i = 0; i < 20 && await page.evaluate(() => location.hash) === '#21'; i++) await page.keyboard.press('ArrowRight');
  await page.waitForTimeout(500);
  await page.keyboard.press('ArrowLeft'); // 5쪽에서 4쪽으로 돌아오면
  await page.waitForTimeout(900);
  const back = await page.screenshot();
  await sideBySide('05-back-finished.png', [
    [fwd, '처음 볼 때', '애니메이션이 하나씩 나와요', '#6A7180'],
    [back, '다시 돌아오면', '완성된 화면이 바로 나와요', RED],
  ]);

  // 6. A 키로 애니메이션 끄기
  await page.evaluate(() => { try { localStorage.removeItem('slides-anim'); } catch (e) {} });
  await open(page, GIT, 8);
  await page.mouse.move(W / 2, H / 2);
  await page.keyboard.press('a');
  await page.waitForTimeout(700);
  const animBtn = await rect(page, '#pl-anim');
  const toast1 = await rect(page, '#pl-toast');
  await annotate(page, [
    { box: pad(toast1, 6) },
    { box: pad(animBtn, 6) },
    { label: 'A 키나 이 버튼으로 끄고 켜요. 끄면 애니메이션 없이 완성된 화면이 나와요. 브라우저가 이 설정을 기억해요', at: { right: W - (animBtn.x + animBtn.w), bottom: H - animBtn.y + 24 }, width: 520 },
  ]);
  await shot(page, '06-animation-off.png');
  await page.keyboard.press('a'); // 다시 켜 둬요
  await page.evaluate(() => { try { localStorage.removeItem('slides-anim'); } catch (e) {} });

  // 7. 숫자 뒤 Enter로 쪽 이동
  await open(page, GIT, 4);
  await page.mouse.move(W / 2, H / 2);
  await page.keyboard.press('2'); await page.keyboard.press('4');
  await page.waitForTimeout(400);
  const toast2 = await rect(page, '#pl-toast');
  const go = await rect(page, '#pl-go');
  await annotate(page, [
    { box: pad(toast2, 6) },
    { label: '쪽 번호를 치고 Enter를 누르면 그 장으로 바로 가요', at: { x: toast2.x + toast2.w + 24, y: toast2.y - 4 }, width: 520, nowrap: true },
    { box: pad(go, 6) },
    { label: '아래 막대의 쪽 번호 칸에 입력해도 돼요', at: { x: go.x, bottom: H - go.y + 24 }, width: 520, nowrap: true },
  ]);
  await shot(page, '07-page-jump.png');
  await page.keyboard.press('Escape');

  // 8. 아래 막대 (기존 키는 그대로)
  await open(page, GIT, 4);
  await page.mouse.move(W / 2, H - 20);
  await page.waitForTimeout(400);
  const bar = await rect(page, '#pl-bar');
  await annotate(page, [
    { box: pad(bar, 0) },
    { label: '마우스를 화면에 올리면 아래 막대가 나타나요. 방향키, Space, N(노트), F(전체 화면)는 전과 같아요', at: { x: W / 2, bottom: H - bar.y + 30 }, anchor: 'translateX(-50%)', width: 1000, nowrap: true },
  ]);
  await shot(page, '08-bottom-bar.png');

  // 0. 한 장 요약 (슬랙 첫 이미지)
  const items = [
    ['페이지 넘김이 화면 양쪽 끝 클릭으로 바뀌었어요', '끝에 마우스를 올리면 화살표가 나타나요'],
    ['글자를 드래그해서 선택할 수 있어요', '선택해도 장이 넘어가지 않아요'],
    ['코드 복사 버튼이 추가되었어요', '터미널은 $ 뒤 명령만, 파이썬은 코드 전체'],
    ['이전 장으로 돌아가면 완성된 화면이 바로 보여요', '처음부터 다시 클릭할 필요가 없어요'],
    ['A 키로 애니메이션을 끌 수 있어요', '브라우저가 설정을 기억해요'],
    ['쪽 번호로 바로 이동할 수 있어요', '쪽 번호를 치고 Enter를 눌러요'],
  ];
  const card = await ctx.newPage();
  await card.setViewportSize({ width: 1600, height: 790 });
  await card.setContent(`<html><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@500;700;900&display=swap"></head>
  <body style="margin:0;background:#F6F5F1;font-family:'Noto Sans KR';color:#1D2330">
  <div style="padding:64px 80px">
    <div style="font-size:24px;font-weight:700;color:#5A3BB8">2026년 11월 3일 · 슬라이드 업데이트</div>
    <div style="font-size:60px;font-weight:900;margin:8px 0 44px">슬라이드 보는 방법이 개선되었어요</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:22px 28px">
    ${items.map(([t, s], i) => `<div style="display:flex;gap:20px;align-items:center;background:#fff;border:2px solid #E1DED6;border-radius:16px;padding:22px 26px">
      <div style="flex:none;width:52px;height:52px;border-radius:50%;background:${RED};color:#fff;font-size:26px;font-weight:900;display:flex;align-items:center;justify-content:center">${i + 1}</div>
      <div><div style="font-size:28px;font-weight:700">${esc(t)}</div><div style="font-size:21px;color:#6A7180;margin-top:4px">${esc(s)}</div></div></div>`).join('')}
    </div>
    <div style="margin-top:36px;font-size:22px;color:#6A7180">방향키, Space, N(노트), F(전체 화면)는 전과 같아요. 01부터 모든 챕터와 번외 슬라이드에 적용돼요.</div>
  </div></body></html>`);
  await card.evaluate(() => document.fonts.ready); await card.waitForTimeout(400);
  await card.screenshot({ path: path.join(OUT, '00-summary.png') });
  await card.close();

  await browser.close();
  console.log('done:', fs.readdirSync(OUT).join(' '));
})();
