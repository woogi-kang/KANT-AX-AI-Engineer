// Builds one self-contained HTML file that plays the deck in a browser with its animations
// (build-ins and magic-move/fade transitions). Usage: node tools/build_player.js slides git-basics-slides.html
const fs = require('fs');
const { renderDeck } = require('./deckrender');
const [dir, out] = process.argv.slice(2);

const PLAYER_CSS = `html,body{margin:0;height:100%;background:#0E1117;overflow:hidden;font-family:'Noto Sans KR',Arial,sans-serif}
#pl-stage{position:absolute;left:50%;top:50%;width:1920px;height:1080px;transform-origin:center center;overflow:hidden;background:#F6F5F1}
#pl-stage>section{position:absolute;left:0;top:0;visibility:hidden}
#pl-stage>section.on{visibility:visible}
[data-build-in]{transition:opacity .45s ease,transform .45s ease}
.pending{opacity:0!important}
.pending.rise{transform:translateY(40px)!important}
.pending.pop{transform:scale(.85)!important}
.hint{position:fixed;top:50%;width:56px;height:56px;margin-top:-28px;padding:0;border:0;border-radius:50%;background:rgba(14,17,23,.6);display:flex;align-items:center;justify-content:center;cursor:pointer;opacity:0;transition:opacity .2s,background .2s}
.hint svg{display:block;width:24px;height:24px}
#pl-hl{left:20px}
#pl-hr{right:20px}
body:hover .hint{opacity:.7}
body:hover .hint:hover{opacity:1;background:rgba(14,17,23,.85)}
#pl-copy{position:fixed;display:none;transform:translateX(-100%);padding:6px 12px;border:1px solid #C9CED8;border-radius:8px;background:#FFFFFF;color:#1D2330;font:500 14px 'Noto Sans KR',Arial,sans-serif;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.2)}
#pl-copy.done{background:#1F8A4C;border-color:#1F8A4C;color:#FFFFFF}
#pl-toast{position:fixed;left:50%;top:24px;transform:translateX(-50%);padding:10px 20px;border-radius:10px;background:rgba(14,17,23,.9);color:#FFFFFF;font-size:18px;opacity:0;transition:opacity .2s;pointer-events:none}
#pl-toast.show{opacity:1}
#pl-bar{position:fixed;left:0;right:0;bottom:0;display:flex;align-items:center;gap:12px;padding:8px 16px;color:#C9CED8;font-size:14px;background:rgba(14,17,23,.85);opacity:0;transition:opacity .2s}
body:hover #pl-bar,#pl-bar:focus-within{opacity:1}
#pl-bar button{background:#252B36;color:#E6E9EF;border:0;border-radius:6px;padding:6px 12px;font:inherit;cursor:pointer}
#pl-bar button.off{background:#5A3BB8}
#pl-bar input{width:72px;background:#252B36;color:#E6E9EF;border:1px solid #3A4250;border-radius:6px;padding:5px 8px;font:inherit}
#pl-bar .grow{flex:1}
#pl-notes{position:fixed;left:16px;right:16px;bottom:52px;max-height:30vh;overflow:auto;padding:16px 20px;border-radius:10px;background:rgba(255,255,255,.96);color:#1D2330;font-size:18px;line-height:1.6;display:none}
#pl-notes.show{display:block}`;

const PLAYER_JS = `
const stage=document.getElementById('pl-stage');
const slides=[...stage.children];
const $=id=>document.getElementById(id);
let cur=0, step=0;
const steps=slides.map(s=>{
  const els=[...s.querySelectorAll('[data-build-in]')];
  const groups=[];let auto=0;
  for(const el of els){
    const spec=el.getAttribute('data-build-in');
    const m=spec.match(/order\\s+(\\d+)/)||spec.match(/\\s(\\d+)$/);
    const k=m?+m[1]:++auto;
    (groups[k]=groups[k]||[]).push(el);
    el.dataset.fx=/rise/.test(spec)?'rise':/pop/.test(spec)?'pop':'fade';
  }
  return groups.filter(Boolean);
});
// seen[i]: how far slide i has been built, so coming back to it does not replay what was already shown
const seen=slides.map(()=>0);
let animOn=true;try{animOn=localStorage.getItem('slides-anim')!=='off';}catch(e){}
function fit(){const s=Math.min(innerWidth/1920,innerHeight/1080);stage._s=s;stage.style.transform='translate(-50%,-50%) scale('+s+')';}
addEventListener('resize',fit);fit();
function setBuild(i,n,animate){
  steps[i].forEach((g,gi)=>g.forEach(el=>{
    if(!animate)el.style.transition='none';
    el.classList.toggle('pending',gi>=n);el.classList.toggle(el.dataset.fx,gi>=n);
    if(!animate){void el.offsetWidth;el.style.transition='';}
  }));
}
function rectIn(el){const r=el.getBoundingClientRect(),S=stage.getBoundingClientRect(),k=stage._s;return{x:(r.left-S.left)/k,y:(r.top-S.top)/k,w:r.width/k,h:r.height/k};}
function topIds(sec){return [...sec.querySelectorAll('[id]')].filter(el=>!el.parentElement.closest('section [id]'));}
function show(n,dir){
  if(n<0||n>=slides.length)return;
  const a=slides[cur],b=slides[n];
  const target=(!animOn||dir<0)?steps[n].length:seen[n];
  setBuild(n,target,false);
  const magic=b.getAttribute('data-transition')==='magic'&&Math.abs(n-cur)===1&&n!==cur;
  if(magic){
    const before={};
    for(const el of topIds(a))before[el.id]={r:rectIn(el),o:getComputedStyle(el).opacity};
    a.classList.remove('on');b.classList.add('on');
    const moved=[];
    for(const el of topIds(b)){
      const p=before[el.id];
      if(!p){el.animate([{opacity:0},{opacity:getComputedStyle(el).opacity}],{duration:450,easing:'ease'});continue;}
      const q=rectIn(el);
      const dx=p.r.x-q.x,dy=p.r.y-q.y,sx=q.w?p.r.w/q.w:1,sy=q.h?p.r.h/q.h:1;
      if(Math.abs(dx)<1&&Math.abs(dy)<1&&Math.abs(sx-1)<.01&&Math.abs(sy-1)<.01&&p.o===getComputedStyle(el).opacity)continue;
      el.animate([{transformOrigin:'0 0',transform:'translate('+dx+'px,'+dy+'px) scale('+sx+','+sy+')',opacity:p.o},{transformOrigin:'0 0',transform:'none',opacity:getComputedStyle(el).opacity}],{duration:700,easing:'cubic-bezier(.4,0,.2,1)'});
    }
  }else{
    a.classList.remove('on');b.classList.add('on');
    if(n!==cur)b.animate([{opacity:0},{opacity:1}],{duration:400,easing:'ease'});
  }
  cur=n;step=target;seen[n]=Math.max(seen[n],step);
  hideCopy();update();
}
function next(){if(animOn&&step<steps[cur].length){step++;seen[cur]=Math.max(seen[cur],step);setBuild(cur,step,true);update();}else show(cur+1,1);}
function prev(){show(cur-1,-1);}
// the on-screen arrows turn the page at once, without stepping through the builds left on this slide
function nextPage(){show(cur+1,1);}
function go(n){n=Math.max(0,Math.min(slides.length-1,n));if(n!==cur)show(n,n<cur?-1:1);}
function update(){
  $('pl-count').textContent=(cur+1)+' / '+slides.length;
  const aside=slides[cur].querySelector('aside');
  $('pl-notes').textContent=aside?aside.textContent:'';
  history.replaceState(null,'','#'+(cur+1));
}
let toastT;
function toast(msg,ms){const t=$('pl-toast');clearTimeout(toastT);if(!msg){t.classList.remove('show');return;}t.textContent=msg;t.classList.add('show');toastT=setTimeout(()=>t.classList.remove('show'),ms||1800);}
function setAnim(on){
  animOn=on;try{localStorage.setItem('slides-anim',on?'on':'off');}catch(e){}
  $('pl-anim').textContent=on?'애니메이션 끄기':'애니메이션 켜기';$('pl-anim').classList.toggle('off',!on);
  if(!on){step=steps[cur].length;seen[cur]=step;setBuild(cur,step,true);}
  toast(on?'애니메이션을 켰어요':'애니메이션을 껐어요. 모든 장을 다 펼쳐서 보여 줘요');update();
}
function fullscreen(){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();}
// Page jump: type the page number, then Enter
let jump='',jumpT;
function setJump(v){jump=v;clearTimeout(jumpT);if(jump){toast(jump+'쪽으로 가려면 Enter',4000);jumpT=setTimeout(()=>{jump='';},4000);}else toast('');}
addEventListener('keydown',e=>{
  if(e.target.closest&&e.target.closest('input'))return;
  if(e.metaKey||e.ctrlKey||e.altKey)return;
  if(/^[0-9]$/.test(e.key)){setJump((jump+e.key).slice(0,3));return;}
  if(jump&&e.key==='Enter'){e.preventDefault();const n=+jump;setJump('');if(n>0)go(n-1);return;}
  if(jump&&e.key==='Backspace'){e.preventDefault();setJump(jump.slice(0,-1));return;}
  if(e.key==='Escape'){setJump('');return;}
  if(['ArrowRight','ArrowDown','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();next();}
  else if(['ArrowLeft','ArrowUp','PageUp','Backspace'].includes(e.key)){e.preventDefault();prev();}
  else if(e.key==='Home')go(0);
  else if(e.key==='End')go(slides.length-1);
  else if(e.key==='n'||e.key==='N')$('pl-notes').classList.toggle('show');
  else if(e.key==='a'||e.key==='A')setAnim(!animOn);
  else if(e.key==='f'||e.key==='F')fullscreen();
});
// Mouse: only the left and right arrow buttons turn the page. Clicks on the slide itself do nothing,
// so text can be selected and copied anywhere.
$('pl-hl').onclick=prev;$('pl-hr').onclick=nextPage;
// Copy button on code blocks: boxes whose text lines are all monospace.
// Terminal blocks copy only the commands after "$ ", other blocks copy every line.
const isMono=el=>/JetBrains/.test(getComputedStyle(el).fontFamily);
function isBox(el){const cs=getComputedStyle(el),c=cs.backgroundColor.match(/[\\d.]+/g);return (c&&(c[3]===undefined||+c[3]>.5))||parseFloat(cs.borderTopWidth)>0;}
function lines(el){return [...el.querySelectorAll('p')].filter(p=>getComputedStyle(p).position!=='absolute');}
const boxes=[...stage.querySelectorAll('section div')].filter(el=>{
  if(!isBox(el))return false;
  const ps=lines(el);
  if(!ps.length||!ps.every(isMono)||el.textContent.trim().length<3)return false;
  // skip small labels such as folder boxes and key caps: keep commands, several lines, or a wide box
  return ps.length>1||/\\$\\s/.test(el.textContent)||el.getBoundingClientRect().width/stage._s>=360;
});
const codes=boxes.filter(b=>!boxes.some(o=>o!==b&&o.contains(b)));
codes.forEach(el=>{if(codeText(el).text.trim())el.dataset.code='';});
function brText(n){return [...n.childNodes].map(c=>c.nodeType===3?c.nodeValue:c.nodeName==='BR'?'\\n':brText(c)).join('');}
function codeText(el){
  const ls=lines(el).flatMap(p=>brText(p).split('\\n')).map(l=>l.replace(/\\u00a0/g,' ').replace(/\\s+$/,''));
  const cmds=ls.map(l=>l.match(/^\\s*(?:\\S*\\s)?\\$\\s+(.+)$/)).filter(Boolean).map(m=>m[1]);
  return cmds.length?{text:cmds.join('\\n'),label:'명령 복사'}:{text:ls.join('\\n').replace(/^\\n+|\\n+$/g,''),label:'복사'};
}
let hovered=null;
const copyBtn=$('pl-copy');
function hideCopy(){hovered=null;copyBtn.style.display='none';}
function showCopy(el){
  if(hovered===el)return;
  hovered=el;const r=el.getBoundingClientRect();
  copyBtn.textContent=codeText(el).label;copyBtn.classList.remove('done');
  copyBtn.style.left=(r.right-8)+'px';copyBtn.style.top=(r.top+8)+'px';copyBtn.style.display='block';
}
addEventListener('mousemove',e=>{
  const t=e.target;
  const onUi=t.closest&&t.closest('#pl-bar,#pl-notes,#pl-copy,.hint');
  if(t===copyBtn)return;
  // find the box by position, because drawings placed over a box can be the event target
  let c=null,area=Infinity;
  if(!onUi)for(const el of slides[cur].querySelectorAll('[data-code]')){
    if(el.closest('.pending'))continue;
    const r=el.getBoundingClientRect();
    if(e.clientX>=r.left&&e.clientX<=r.right&&e.clientY>=r.top&&e.clientY<=r.bottom&&r.width*r.height<area){c=el;area=r.width*r.height;}
  }
  if(c)showCopy(c);else hideCopy();
});
async function writeClip(text){
  try{await navigator.clipboard.writeText(text);return true;}catch(e){}
  const ta=document.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();
  let ok=false;try{ok=document.execCommand('copy');}catch(e){}
  ta.remove();return ok;
}
copyBtn.onclick=async()=>{
  if(!hovered)return;
  const ok=await writeClip(codeText(hovered).text);
  copyBtn.textContent=ok?'복사했어요':'복사가 안 돼요. 끌어서 골라 주세요';copyBtn.classList.toggle('done',ok);
};
$('pl-prev').onclick=prev;$('pl-next').onclick=next;
// a clicked button keeps focus, and Space or Enter would press it again on top of the key's own action
for(const btn of document.querySelectorAll('button'))btn.addEventListener('click',()=>btn.blur());
addEventListener('hashchange',()=>{const n=parseInt(location.hash.slice(1));if(n>0)go(n-1);});
addEventListener('resize',hideCopy);
$('pl-nb').onclick=()=>$('pl-notes').classList.toggle('show');
$('pl-fs').onclick=fullscreen;
$('pl-anim').onclick=()=>setAnim(!animOn);
$('pl-go').addEventListener('keydown',e=>{
  if(e.key==='Enter'){const n=parseInt(e.target.value);e.target.value='';e.target.blur();if(n>0)go(n-1);}
  else if(e.key==='Escape'){e.target.value='';e.target.blur();}
});
let tx=null;addEventListener('touchstart',e=>tx=e.touches[0].clientX);addEventListener('touchend',e=>{if(tx===null)return;const d=e.changedTouches[0].clientX-tx;if(Math.abs(d)>40)(d<0?next:prev)();tx=null;});
const start=Math.max(0,Math.min(slides.length-1,(parseInt(location.hash.slice(1))||1)-1));
slides.forEach((s,i)=>setBuild(i,0,false));
cur=start;step=animOn?0:steps[cur].length;seen[cur]=step;setBuild(cur,step,false);
$('pl-anim').textContent=animOn?'애니메이션 끄기':'애니메이션 켜기';$('pl-anim').classList.toggle('off',!animOn);
slides[cur].classList.add('on');update();
`;

(async () => {
  const { deck, browser, page, FONTS, BASE_CSS } = await renderDeck(dir);
  const sections = await page.evaluate(() => [...document.querySelectorAll('body > section')].map(s => s.outerHTML).join('\n'));
  await browser.close();
  const title = deck.title || 'Slides';
  const html = `<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${title}</title>
<link rel="stylesheet" href="${FONTS}">
<style>${BASE_CSS}
${PLAYER_CSS}</style></head>
<body>
<div id="pl-stage">
${sections}
</div>
<button id="pl-hl" class="hint" aria-label="이전 쪽"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15,5 8,12 15,19"/></svg></button><button id="pl-hr" class="hint" aria-label="다음 쪽"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9,5 16,12 9,19"/></svg></button>
<button id="pl-copy"></button>
<div id="pl-toast"></div>
<div id="pl-notes"></div>
<div id="pl-bar"><button id="pl-prev">이전</button><button id="pl-next">다음</button><span id="pl-count"></span><input id="pl-go" inputmode="numeric" placeholder="쪽 번호" aria-label="쪽 번호로 가기"><span class="grow"></span><span>→ 다음 · ← 이전 · 숫자+Enter 쪽 이동 · A 애니메이션 · N 노트 · F 전체 화면</span><button id="pl-anim">애니메이션 끄기</button><button id="pl-nb">노트</button><button id="pl-fs">전체 화면</button></div>
<script>${PLAYER_JS}</script>
</body></html>`;
  fs.writeFileSync(out, html);
  console.log(`${deck.order.length} slides -> ${out} (${(html.length / 1024).toFixed(0)} KB)`);
})();
