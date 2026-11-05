// 붕어빵 기계 (24): pick a flavor and a price, then press the buttons to run a = Bread("팥", 1000) one step at a time.
// Runs inside the slide player as function(sec, api). gen.py inlines this file into the lab slide.
const $ = id => sec.querySelector('#' + id);
const MONO = "'JetBrains Mono','Noto Sans KR',monospace";
const NAMES = ['a', 'b', 'c', 'd'];
const LINE_Y = [0, 0, 58, 116, 174, 232, 290];   // top of code line 1..6 inside the code panel
let flavor = '팥', price = 1000, made = [], step = 0, timer = null, card = null;

const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
function pickRow(rowId, value) {
  for (const b of $(rowId).querySelectorAll('button')) b.classList.toggle('lb-on', b.dataset.v === String(value));
}
function name() { return NAMES[made.length % NAMES.length]; }
function callLine() {
  $('lb-call').innerHTML = `<span style="color:#F2C48D">${name()}</span><span style="color:#E6E9EF"> = Bread(</span>`
    + `<span id="lb-argf" style="color:#8FD8DE">"${esc(flavor)}"</span><span style="color:#E6E9EF">, </span>`
    + `<span id="lb-argp" style="color:#8FD8DE">${price}</span><span style="color:#E6E9EF">)</span>`;
}
function mark(line) {
  const hl = $('lb-hl');
  if (!line) { hl.style.opacity = 0; return; }
  hl.style.opacity = 1; hl.style.top = (24 + LINE_Y[line]) + 'px';
}
function msg(n, text) {
  $('lb-msg').innerHTML = n ? `<b style="color:#0F7C86;font-size:34px;margin-right:14px">${'①②③④⑤'[n - 1]}</b>${text}` : text;
}
function row(k, v) {
  return `<div class="lb-row" style="height:60px;display:flex;align-items:center;gap:14px;border-radius:12px;background:#FBF0E0;border:2px solid #E1DED6;padding:0 16px;animation:lbPop .5s ease">`
    + `<p style="width:42%;font-family:${MONO};font-size:24px;font-weight:700;color:#4A5262">${k}</p>`
    + `<p style="flex:1;font-family:${MONO};font-size:28px;font-weight:700;color:#1D2330">${esc(v)}</p></div>`;
}
function newCard() {
  const c = document.createElement('div');
  c.style.cssText = 'position:absolute;left:1300px;top:420px;width:480px;background:#FFFFFF;border:3px solid #9A5B13;border-radius:26px;overflow:hidden;animation:lbPop .5s ease;transition:all .8s cubic-bezier(.4,0,.2,1)';
  c.innerHTML = `<div style="height:66px;background:#9A5B13;display:flex;align-items:center;padding:0 24px;gap:14px">`
    + `<p class="lb-nm" style="font-family:${MONO};font-size:32px;font-weight:700;color:#FFFFFF">?</p><div style="flex:1"></div>`
    + `<p style="font-size:20px;font-weight:700;color:#FFFFFF;opacity:.85">Bread 붕어빵</p></div>`
    + `<div class="lb-rows" style="padding:14px 20px;display:flex;flex-direction:column;gap:8px;min-height:88px">`
    + `<p class="lb-empty" style="height:60px;font-size:24px;color:#6A7180;line-height:60px;text-align:center">아직 칸이 없어요</p></div>`;
  sec.appendChild(c);
  return c;
}
function addRow(k, v) {
  const box = card.querySelector('.lb-rows');
  const e = card.querySelector('.lb-empty'); if (e) e.remove();
  box.insertAdjacentHTML('beforeend', row(k, v));
}
function tray() {
  $('lb-tray').innerHTML = made.map(m => `<div style="width:190px;height:118px;flex:none;background:#FFFFFF;border:3px solid #9A5B13;border-radius:18px;overflow:hidden;animation:lbPop .5s ease">`
    + `<p style="height:40px;background:#9A5B13;color:#FFFFFF;font-family:${MONO};font-size:24px;font-weight:700;line-height:40px;padding:0 14px">${m.name}</p>`
    + `<p style="font-family:${MONO};font-size:20px;font-weight:700;color:#1D2330;padding:8px 14px 0">"${esc(m.flavor)}"</p>`
    + `<p style="font-family:${MONO};font-size:20px;font-weight:700;color:#1D2330;padding:0 14px">${m.price}</p></div>`).join('')
    || `<p style="font-size:24px;color:#6A7180">아직 없어요. 찍으면 여기에 쌓여요.</p>`;
  $('lb-count').textContent = made.length ? `${made.length}개` : '';
}
function setLocals(on) {
  $('lb-locals').style.opacity = on ? 1 : 0;
  $('lb-lf').textContent = `"${flavor}"`; $('lb-lp').textContent = price;
}
function setSelf(on) { $('lb-self').style.opacity = on ? 1 : 0; }
function lock(on) { for (const b of sec.querySelectorAll('.lb-pick button')) b.disabled = on; }

function advance() {
  if (step === 5) { finishCard(); buttons(); return; }
  step++;
  if (step === 1) {
    lock(true); callLine(); mark(6); card = newCard();
    msg(1, `<code>${name()} = Bread("${esc(flavor)}", ${price})</code>를 실행해요. 먼저 빈 붕어빵이 하나 생겨요.`);
  } else if (step === 2) {
    mark(2); setSelf(true); setLocals(true); card.querySelector('.lb-nm').textContent = 'self';
    msg(2, '파이썬이 빈 붕어빵을 <b>self</b>에, 재료를 flavor와 price에 넣어 __init__을 불러요.');
  } else if (step === 3) {
    mark(3); addRow('flavor', `"${flavor}"`);
    msg(3, '<code>self.flavor = flavor</code>: self가 가리키는 붕어빵에 맛 칸을 붙여요.');
  } else if (step === 4) {
    mark(4); addRow('price', String(price));
    msg(4, '<code>self.price = price</code>: 가격 칸도 붙여요.');
  } else if (step === 5) {
    mark(6); setSelf(false); setLocals(false); card.querySelector('.lb-nm').textContent = name();
    msg(5, `__init__이 끝나요. 재료(지역 변수)는 사라지고, 다 된 붕어빵에 <b>${name()}</b>라는 이름이 붙어요.`);
  }
  buttons();
}
function finishCard() {
  made.push({ name: name(), flavor, price });
  if (made.length > NAMES.length) made = made.slice(-1);
  if (card) { const c = card; c.style.opacity = 0; c.style.transform = 'translateY(260px) scale(.4)'; setTimeout(() => c.remove(), 800); card = null; }
  step = 0; mark(0); lock(false); tray(); callLine();
  msg(0, made.length >= NAMES.length ? '틀 하나로 붕어빵 네 개를 찍었어요. 처음부터를 누르면 다시 시작해요.' : '다른 맛과 가격을 골라 한 번 더 찍어 봐요. self는 이번엔 새 붕어빵을 가리켜요.');
}
function stop() { clearInterval(timer); timer = null; }
function auto() {
  stop();
  if (step === 5) finishCard();
  advance();
  timer = setInterval(() => { if (step >= 5) { stop(); buttons(); return; } advance(); }, 1300);
  buttons();
}
function buttons() {
  const full = made.length >= NAMES.length && step === 0;
  $('lb-next').textContent = step === 0 ? '한 단계씩 ▶' : step === 5 ? '쟁반에 담기 ▶' : '다음 단계 ▶';
  $('lb-next').disabled = !!timer || full;
  $('lb-auto').disabled = !!timer || full;
}
function reset() {
  stop(); if (card) card.remove(); card = null; made = []; step = 0;
  mark(0); setSelf(false); setLocals(false); lock(false); tray(); callLine(); buttons();
  msg(0, '맛과 가격을 고르고 <b>한 단계씩</b>이나 <b>한 번에 찍기</b>를 눌러요.');
}
for (const b of sec.querySelectorAll('#lb-flavors button')) b.onclick = () => { flavor = b.dataset.v; pickRow('lb-flavors', flavor); callLine(); };
for (const b of sec.querySelectorAll('#lb-prices button')) b.onclick = () => { price = +b.dataset.v; pickRow('lb-prices', price); callLine(); };
$('lb-next').onclick = () => { stop(); advance(); };
$('lb-auto').onclick = auto;
$('lb-reset').onclick = reset;
reset();
return { leave: stop };
