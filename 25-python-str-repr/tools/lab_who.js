// 누가 불릴까 (25): switch __str__ and __repr__ on or off, press a way of showing a, and watch which method Python
// looks for, in order, before the output appears. Runs inside the slide player as function(sec, api).
// The outputs are the ones the real kernel printed in tools/demo.sh (the 0x addresses change every run).
const $ = id => sec.querySelector('#' + id);
const has = { str: true, repr: true };
const OBJ = { a: ['팥', 1000, '0x7f6735bb38c0'], b: ['슈크림', 1200, '0x7f6735dc4a50'] };
const won = n => n.toLocaleString('en-US');
const FX = {
  str: k => `${OBJ[k][0]} 붕어빵 ${won(OBJ[k][1])}원`,
  repr: k => `Bread('${OBJ[k][0]}', ${OBJ[k][1]})`,
  base: (k, cell) => `<__main__.Bread ${cell ? '' : 'object '}at ${OBJ[k][2]}>`,
};
// what each button asks Python for: the methods it tries in order, and how the found text is put together
const ASK = {
  print: { order: ['str', 'repr', 'base'], show: f => f('a'), why: 'print는 글자가 필요해서 __str__부터 찾아요.' },
  fstr: { order: ['str', 'repr', 'base'], show: f => '주문: ' + f('a'), why: 'f-string 중괄호도 글자가 필요해서 __str__부터 찾아요.' },
  cell: { order: ['repr', 'base'], cell: true, show: f => f('a'), why: '셀 마지막 줄은 만든 사람이 보는 곳이라 __repr__만 찾아요. __str__은 보지 않아요.' },
  list: { order: ['repr', 'base'], show: f => `[${f('a')}, ${f('b')}]`, why: '리스트는 안의 a, b를 __repr__로 보여 줘요. __str__은 보지 않아요.' },
};
let busy = false, timers = [];
const later = (ms, fn) => timers.push(setTimeout(fn, ms));
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');

function paintCode() {
  for (const k of ['str', 'repr']) {
    const blk = $('lw-' + k);
    blk.style.opacity = has[k] ? 1 : .28;
    blk.style.textDecoration = has[k] ? 'none' : 'line-through';
    $('lw-t-' + k).textContent = has[k] ? '있음' : '없음';
    $('lw-t-' + k).parentElement.classList.toggle('lw-off', !has[k]);
  }
}
function lane(state) {
  for (const k of ['str', 'repr', 'base']) {
    const box = $('lw-l-' + k), st = state[k] || 'idle';
    box.dataset.st = st;
    $('lw-s-' + k).textContent = { idle: '', skip: '안 봐요', look: '찾는 중', no: '없어요', yes: '찾았어요' }[st];
  }
}
function glow(k) {
  for (const x of ['str', 'repr']) $('lw-' + x).style.background = x === k ? 'rgba(242,196,141,.22)' : 'transparent';
}
function out(text, cell) {
  // the whole line at once, faded in (no letter-by-letter typing)
  $('lw-n').textContent = cell ? 'Out' : '';
  const el = $('lw-out');
  el.style.opacity = 0; el.textContent = text;
  later(20, () => { el.style.opacity = 1; });
}
function run(kind) {
  if (busy) return;
  busy = true; lockButtons(true);
  const ask = ASK[kind];
  for (const b of sec.querySelectorAll('#lw-asks button')) b.classList.toggle('lw-on', b.dataset.k === kind);
  const state = {}; for (const k of ['str', 'repr', 'base']) if (!ask.order.includes(k)) state[k] = 'skip';
  lane(state); glow(null); $('lw-out').textContent = ''; $('lw-n').textContent = '';
  $('lw-msg').textContent = ask.why;
  let t = 300;
  for (const k of ask.order) {
    const found = k === 'base' || has[k];
    later(t, () => { state[k] = 'look'; lane(state); });
    t += 650;
    later(t, () => { state[k] = found ? 'yes' : 'no'; lane(state); if (found && k !== 'base') glow(k); });
    t += 450;
    if (found) {
      later(t, () => {
        out(ask.show(x => k === 'base' ? FX.base(x, ask.cell) : FX[k](x)), ask.cell);
        $('lw-msg').textContent = k === 'base'
          ? '틀에 없어서 파이썬이 정한 기본 모양을 써요. 주소는 실행할 때마다 달라요.'
          : `틀의 ${k === 'str' ? '__str__' : '__repr__'}이 돌려준 글자를 보여 줘요.`;
        busy = false; lockButtons(false);
      });
      break;
    }
  }
}
function lockButtons(on) { for (const b of sec.querySelectorAll('button')) b.disabled = on; }
function stop() { timers.forEach(clearTimeout); timers = []; busy = false; lockButtons(false); }
for (const k of ['str', 'repr']) $('lw-t-' + k).parentElement.onclick = () => { has[k] = !has[k]; paintCode(); lane({}); glow(null); };
for (const b of sec.querySelectorAll('#lw-asks button')) b.onclick = () => run(b.dataset.k);
paintCode(); lane({});
return { leave: stop };
