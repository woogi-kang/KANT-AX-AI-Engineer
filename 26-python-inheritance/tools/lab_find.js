// 메서드 찾기 (26): pick a 붕어빵 and what to ask it for, then watch Python look in the 붕어빵, its 틀 and the
// parent 틀, in that order. Runs inside the slide player as function(sec, api).
// The outputs are the ones the real kernel printed in tools/demo.sh (the last run in tools/run_nb.py).
const $ = id => sec.querySelector('#' + id);
const OBJS = { a: { cls: 'Bread', attrs: ['flavor', 'price'] }, c: { cls: 'CreamBread', attrs: ['flavor', 'price', 'cream'] } };
const CLS = { CreamBread: { parent: 'Bread', attrs: ['__init__', 'intro', 'keep'] }, Bread: { parent: null, attrs: ['shop', '__init__', 'intro'] } };
const METHOD = { intro: true, keep: true };
const JOSA = { intro: '가', keep: '이', shop: '이', cream: '이', flavor: '가' };   // 인트로가, 킵이, 숍이, 크림이, 플레이버가
const OUT = {
  'a.intro': '팥 붕어빵 1000 원', 'c.intro': '슈크림 붕어빵 1200 원\n  크림: 많이',
  'a.keep': "AttributeError: 'Bread' object has no attribute 'keep'", 'c.keep': '슈크림 붕어빵은 차갑게 보관해요',
  'a.shop': '붕어빵 1호점', 'c.shop': '붕어빵 1호점',
  'a.cream': "AttributeError: 'Bread' object has no attribute 'cream'", 'c.cream': '많이',
  'a.flavor': '팥', 'c.flavor': '슈크림',
};
let who = 'c', what = 'intro', timers = [], busy = false;
const later = (ms, fn) => timers.push(setTimeout(fn, ms));
const code = () => METHOD[what] ? `${who}.${what}()` : `print(${who}.${what})`;

function clear() {
  for (const el of sec.querySelectorAll('.lf-look,.lf-yes,.lf-no,.lf-super')) el.classList.remove('lf-look', 'lf-yes', 'lf-no', 'lf-super');
  $('lf-log').innerHTML = ''; $('lf-out').textContent = ''; $('lf-out').style.color = '#1D2330';
}
function pick() {
  for (const b of sec.querySelectorAll('#lf-who button')) b.classList.toggle('lf-on', b.dataset.o === who);
  for (const b of sec.querySelectorAll('#lf-what button')) b.classList.toggle('lf-on', b.dataset.k === what);
  $('lf-code').textContent = code();
}
function log(n, text, ok) {
  $('lf-log').insertAdjacentHTML('beforeend', `<p style="font-size:25px;line-height:1.45;color:#1D2330;animation:lfIn .35s ease">`
    + `<b style="color:#2F7D6B;margin-right:10px">${'①②③④'[n]}</b>${text}`
    + (ok === undefined ? '' : ` <b style="color:${ok ? '#1F8A4C' : '#A33131'}">${ok ? '있어요' : '없어요'}</b>`) + '</p>');
}
function lock(on) { busy = on; for (const b of sec.querySelectorAll('button')) b.disabled = on; }
function run() {
  if (busy) return;
  clear(); lock(true);
  const o = OBJS[who];
  const places = [{ el: 'lf-o-' + who, name: `${who} 붕어빵`, has: o.attrs, row: k => `lf-o-${who}-${k}` }];
  for (let c = o.cls; c; c = CLS[c].parent) places.push({ el: 'lf-m-' + c, name: `${c} 틀`, has: CLS[c].attrs, row: k => `lf-m-${c}-${k}` });
  let t = 250, n = 0, found = null;
  for (const pl of places) {
    const hit = pl.has.includes(what), i = n++;
    later(t, () => $(pl.el).classList.add('lf-look'));
    t += 600;
    later(t, () => {
      $(pl.el).classList.remove('lf-look');
      $(pl.el).classList.add(hit ? 'lf-yes' : 'lf-no');
      if (hit) $(pl.row(what)).classList.add('lf-yes');
      log(i, `${pl.name}에 <code>${what}</code>${JOSA[what]} 있나요?`, hit);
    });
    t += 500;
    if (hit) { found = pl; break; }
  }
  if (found && who === 'c' && what === 'intro') {
    later(t, () => { $('lf-m-Bread-intro').classList.add('lf-super'); log(n, '자식의 intro 안에서 <code>super().intro()</code>로 부모 Bread의 intro도 불러요.'); });
    t += 900;
  }
  later(t, () => {
    const out = OUT[who + '.' + what];
    $('lf-out').textContent = out;
    if (!found) $('lf-out').style.color = '#A33131';
    $('lf-msg').innerHTML = !found
      ? `Bread 틀까지 찾아도 없어서 AttributeError가 나요. ${who === 'a' ? 'a는 Bread로 찍어서 자식 틀 CreamBread는 보지 않아요.' : ''}`
      : found.el.startsWith('lf-o-') ? '붕어빵에 붙은 칸이라 붕어빵에서 바로 찾았어요.'
      : found.name === `${OBJS[who].cls} 틀` ? '붕어빵에는 없어서, 그 붕어빵을 찍은 틀에서 찾았어요.'
      : '자기 틀에도 없어서 부모 틀까지 올라가 찾았어요. 물려받은 거예요.';
    lock(false);
  });
}
function stop() { timers.forEach(clearTimeout); timers = []; lock(false); }
for (const b of sec.querySelectorAll('#lf-who button')) b.onclick = () => { who = b.dataset.o; pick(); clear(); };
for (const b of sec.querySelectorAll('#lf-what button')) b.onclick = () => { what = b.dataset.k; pick(); clear(); };
$('lf-go').onclick = run;
pick();
return { leave: stop };
