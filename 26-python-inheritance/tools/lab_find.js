// 메서드 찾기 (26): pick an object (a = Animal, d = Dog) and what to ask it for, then watch Python look in the
// object, its class and the parent class, in that order. Runs inside the slide player as function(sec, api).
// The outputs are the ones the real kernel printed in tools/demo.sh (the last run in tools/run_nb.py).
const $ = id => sec.querySelector('#' + id);
const OBJS = { a: { cls: 'Animal', attrs: ['name'] }, d: { cls: 'Dog', attrs: ['name', 'breed'] } };
const CLS = { Dog: { parent: 'Animal', attrs: ['__init__', 'speak', 'fetch'] }, Animal: { parent: null, attrs: ['__init__', 'eat', 'speak'] } };
const METHOD = { speak: true, eat: true, fetch: true };
const JOSA = { speak: '가', eat: '이', fetch: '가', breed: '가', name: '이' };   // 스피크가, 잇이, 페치가, 브리드가, 네임이
const OUT = {
  'a.speak': '하마가 소리를 내요', 'd.speak': '초코가 멍멍 짖어요',
  'a.eat': '하마가 밥을 먹어요', 'd.eat': '초코가 밥을 먹어요',
  'a.fetch': "AttributeError: 'Animal' object has no attribute 'fetch'", 'd.fetch': '초코가 공을 물어 와요',
  'a.breed': "AttributeError: 'Animal' object has no attribute 'breed'", 'd.breed': '푸들',
  'a.name': '하마', 'd.name': '초코',
};
let who = 'd', what = 'eat', timers = [], busy = false;
const later = (ms, fn) => timers.push(setTimeout(fn, ms));
const code = () => METHOD[what] ? `${who}.${what}()` : `print(${who}.${what})`;

function clear() {
  for (const el of sec.querySelectorAll('.lf-look,.lf-yes,.lf-no')) el.classList.remove('lf-look', 'lf-yes', 'lf-no');
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
  const places = [{ el: 'lf-o-' + who, name: `${who} 객체`, has: o.attrs, row: k => `lf-o-${who}-${k}` }];
  for (let c = o.cls; c; c = CLS[c].parent) places.push({ el: 'lf-m-' + c, name: `${c} 클래스`, has: CLS[c].attrs, row: k => `lf-m-${c}-${k}` });
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
  later(t, () => {
    const out = OUT[who + '.' + what];
    $('lf-out').textContent = out;
    if (!found) $('lf-out').style.color = '#A33131';
    $('lf-msg').innerHTML = !found
      ? `Animal 클래스까지 찾아도 없어서 AttributeError가 나요. ${who === 'a' ? 'a는 Animal로 만들어서 자식 클래스 Dog는 보지 않아요.' : ''}`
      : found.el.startsWith('lf-o-') ? '객체에 붙은 칸이라 객체에서 바로 찾았어요.'
      : found.name === `${OBJS[who].cls} 클래스` ? (who === 'd' && what === 'speak' ? 'Dog에서 찾아서 Animal까지 가지 않아요. 덮어쓴 speak예요.' : '객체에는 없어서, 그 객체를 만든 클래스에서 찾았어요.')
      : '자기 클래스에도 없어서 부모 클래스까지 올라가 찾았어요. 물려받은 거예요.';
    lock(false);
  });
}
function stop() { timers.forEach(clearTimeout); timers = []; lock(false); }
for (const b of sec.querySelectorAll('#lf-who button')) b.onclick = () => { who = b.dataset.o; pick(); clear(); };
for (const b of sec.querySelectorAll('#lf-what button')) b.onclick = () => { what = b.dataset.k; pick(); clear(); };
$('lf-go').onclick = run;
pick();
return { leave: stop };
