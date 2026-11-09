// 릴리스 노트에 넣을 전후 비교 스크린샷을 실제 덱으로 찍어요.
// 사용법 (레포 맨 위에서): node updates/2026-11-09-deck-redesign/tools/shots.js
// "전" 화면은 다시 만들기 전 main 커밋(BEFORE_REV, 기본 4c4189d)의 HTML을 git에서 꺼내 찍어요.
const { chromium } = require('playwright');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const ROOT = path.resolve(__dirname, '../../..');
const OUT = path.resolve(__dirname, '../img');
const REV = process.env.BEFORE_REV || '4c4189d';
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'before-'));
const W = 1600, H = 900;

// [파일 이름, 덱 경로, 쪽 번호, 전 설명, 후 설명]
const PAIRS = [
  ['01-focus.png', '24-python-class/python-class-slides.html', 5, '설명 카드 네 개가 그림과 나란히 있었어요', '그림을 크게 두고 이름을 바로 옆에 붙였어요'],
  ['02-code.png', '02-git-basics/git-basics-slides.html', 12, '터미널 글씨가 작았어요', '터미널을 넓히고 글씨를 키웠어요'],
  ['03-title.png', '02-git-basics/git-basics-slides.html', 24, '제목이 명령어였어요', '제목만 읽어도 무슨 일인지 알아요'],
];

function before(rel) {
  const f = path.join(TMP, rel);
  fs.mkdirSync(path.dirname(f), { recursive: true });
  fs.writeFileSync(f, execSync(`git show ${REV}:${rel}`, { cwd: ROOT, maxBuffer: 64 << 20 }));
  return f;
}
async function capture(page, file, n) {
  await page.goto('about:blank');
  await page.goto('file://' + file + '#' + n);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);
  // 애니메이션을 끝까지 펼친 완성된 화면을 찍어요
  for (let i = 0; i < 30; i++) {
    if (!(await page.evaluate(() => document.querySelectorAll('#pl-stage>section.on .pending').length))) break;
    await page.keyboard.press('Space');
    await page.waitForTimeout(120);
  }
  // 슬라이드 내용만 보이게 아래 막대와 양옆 화살표를 숨겨요
  await page.addStyleTag({ content: '#pl-bar,#pl-hl,#pl-hr{display:none!important}' });
  await page.waitForTimeout(700);
  return page.screenshot();
}
async function sideBySide(ctx, name, a, b, ta, tb) {
  const p = await ctx.newPage();
  await p.setViewportSize({ width: 1600, height: 100 });
  const img = x => 'data:image/png;base64,' + x.toString('base64');
  const panel = (x, t, sub, c) => `<div style="flex:1;display:flex;flex-direction:column;gap:14px">
    <div style="font-size:28px;font-weight:700;color:${c}">${t} <span style="font-weight:500;color:#1D2330">· ${sub}</span></div>
    <img src="${img(x)}" style="width:100%;border-radius:12px;border:4px solid ${c};box-sizing:border-box"></div>`;
  await p.setContent(`<html><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@500;700&display=swap"></head>
  <body style="margin:0;background:#F6F5F1;font-family:'Noto Sans KR'">
  <div style="display:flex;gap:56px;padding:36px 40px;align-items:flex-start">
  ${panel(a, '전', ta, '#6A7180')}
  <div style="align-self:center;font-size:44px;color:#1D2330;margin:40px -40px 0">&#8594;</div>
  ${panel(b, '후', tb, '#1F8A4C')}
  </div></body></html>`);
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
  await p.screenshot({ path: path.join(OUT, name), fullPage: true });
  await p.close();
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: W, height: H } });
  const page = await ctx.newPage();
  for (const [name, rel, n, ta, tb] of PAIRS) {
    const a = await capture(page, before(rel), n);
    const b = await capture(page, path.join(ROOT, rel), n);
    await sideBySide(ctx, name, a, b, ta, tb);
    console.log('saved', name);
  }
  await browser.close();
  fs.rmSync(TMP, { recursive: true, force: true });
})();
