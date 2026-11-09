// 이름 바꾸기 (27): pick the name written inside the class and the name used outside, then run.
// The slide shows the name Python stores (__dict__) and what print prints. Runs inside the slide player as function(sec, api).
// Every output is one the real kernel printed in tools/demo.sh (the 눌러 보기 runs in tools/run_nb.py).
const $ = id => sec.querySelector('#' + id);
const STORED = { password: 'password', _password: '_password', __password: '_Secret__password' };
const MSG = {
  password: '밑줄 없는 이름은 그대로 저장돼요.',
  _password: '밑줄 하나는 이름이 그대로예요. 표시만 붙은 거예요.',
  __password: '밑줄 두 개는 앞에 _Secret이 붙어서 저장돼요.',
};
let inside = '__password', outside = '__password', timers = [], busy = false;
const later = (ms, fn) => timers.push(setTimeout(fn, ms));
function pick() {
  for (const b of sec.querySelectorAll('#ln-in button')) b.classList.toggle('ln-on', b.dataset.n === inside);
  for (const b of sec.querySelectorAll('#ln-out button')) b.classList.toggle('ln-on', b.dataset.n === outside);
  $('ln-code-in').textContent = `        self.${inside} = 1234`;
  $('ln-code-out').textContent = `print(mypass.${outside})`;
}
function clear() {
  $('ln-dict').textContent = '';
  $('ln-res').textContent = '';
  $('ln-dict-box').classList.remove('ln-show');
  $('ln-res-box').classList.remove('ln-show', 'ln-ok', 'ln-bad');
}
function lock(on) { busy = on; for (const b of sec.querySelectorAll('button')) b.disabled = on; }
function run() {
  if (busy) return;
  clear(); lock(true);
  const st = STORED[inside], ok = st === outside;
  later(200, () => { $('ln-dict').textContent = `{'${st}': 1234}`; $('ln-dict-box').classList.add('ln-show'); $('ln-msg').textContent = MSG[inside]; });
  later(1100, () => {
    $('ln-res').textContent = ok ? '1234' : `AttributeError: 'Secret' object has no attribute '${outside}'`;
    $('ln-res-box').classList.add('ln-show', ok ? 'ln-ok' : 'ln-bad');
    $('ln-msg').textContent = MSG[inside] + (ok ? ' 저장된 이름과 똑같이 적어서 찾았어요.' : ` 저장된 이름은 ${st}라서 ${outside}로는 못 찾아요.`);
    lock(false);
  });
}
function stop() { timers.forEach(clearTimeout); timers = []; lock(false); }
for (const b of sec.querySelectorAll('#ln-in button')) b.onclick = () => { inside = b.dataset.n; pick(); clear(); };
for (const b of sec.querySelectorAll('#ln-out button')) b.onclick = () => { outside = b.dataset.n; pick(); clear(); };
$('ln-go').onclick = run;
pick();
return { leave: stop };
