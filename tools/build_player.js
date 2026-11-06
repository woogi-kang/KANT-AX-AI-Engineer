// Builds one self-contained HTML file that plays the deck in a browser with its animations
// (build-ins and magic-move/fade transitions). Usage: node tools/build_player.js slides git-basics-slides.html
// Extras a slide can use, both ignored by check.js and export.js so the PDF shows the slide's plain layout:
// - data-build-in="fly order N" data-from="someId": the element flies in from where #someId is drawn.
// - highlights (see tools/HIGHLIGHT.md): data-build-in="draw order N" on an SVG draws its strokes like a pen;
//   "type order N" types the text in; "spot order N" on an empty box dims the slide except that box, and the
//   hole slides to the next "spot" box ("spot-off" clears it); "cursor order N" / "click order N" on an empty box
//   moves a mouse pointer there (click adds a ripple), "cursor-off" hides it. spot, cursor and click may name
//   data-target="someId" to use that element's box instead of their own.
// - <script type="text/slide-js"> inside a section: run once as function(sec, api) when the player loads.
//   It may return {enter(), leave(), step(n, animate)}; enter runs when the slide is shown, leave when another
//   slide is shown, step after each build. Use it for buttons students press on the slide.
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
#pl-notes.show{display:block}
[data-build-in^="spot"],[data-build-in^="cursor"],[data-build-in^="click"]{visibility:hidden}
[data-build-in^="draw"]{stroke-dasharray:1;transition:opacity .45s ease,stroke-dashoffset .7s cubic-bezier(.6,0,.3,1)}
.pending.draw{opacity:1!important;stroke-dashoffset:1}
.pl-spot{position:absolute;z-index:40;pointer-events:none;border-radius:18px;opacity:0;box-shadow:0 0 0 4px rgba(255,255,255,.92),0 0 0 4000px rgba(10,12,18,.62);transition:left .6s cubic-bezier(.65,0,.35,1),top .6s cubic-bezier(.65,0,.35,1),width .6s cubic-bezier(.65,0,.35,1),height .6s cubic-bezier(.65,0,.35,1),opacity .4s ease}
.pl-spot.on{opacity:1}
.pl-cur{position:absolute;z-index:45;width:40px;height:56px;margin:-4px 0 0 -6px;pointer-events:none;opacity:0;transition:left .8s cubic-bezier(.65,0,.35,1),top .8s cubic-bezier(.65,0,.35,1),opacity .3s ease}
.pl-cur.on{opacity:1}
.pl-rip{position:absolute;z-index:44;width:40px;height:40px;margin:-20px 0 0 -20px;border-radius:50%;border:5px solid #2459C9;opacity:0;pointer-events:none}
.pl-rip.go{animation:pl-rip .6s ease-out}
@keyframes pl-rip{0%{opacity:.9;transform:scale(.4)}100%{opacity:0;transform:scale(3)}}`;

const PLAYER_JS = `
const stage=document.getElementById('pl-stage');
const slides=[...stage.children];
const $=id=>document.getElementById(id);
let cur=0, step=0;
const HL_KINDS=['draw','type','spot','spot-off','cursor','click','cursor-off'];
const steps=slides.map(s=>{
  const els=[...s.querySelectorAll('[data-build-in]')];
  const groups=[];let auto=0;
  for(const el of els){
    const spec=el.getAttribute('data-build-in');
    const m=spec.match(/order\\s+(\\d+)/)||spec.match(/\\s(\\d+)$/);
    const k=m?+m[1]:++auto;
    (groups[k]=groups[k]||[]).push(el);
    const kind=spec.trim().split(/\\s+/)[0];
    el.dataset.fx=HL_KINDS.includes(kind)?kind:/rise/.test(spec)?'rise':/pop/.test(spec)?'pop':/fly/.test(spec)?'fly':'fade';
    if(kind==='draw')[el,...el.querySelectorAll('path,rect,circle,ellipse,line,polyline,polygon')].forEach(x=>x.setAttribute('pathLength','1'));
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
    const was=el.classList.contains('pending');
    const fly=animate&&was&&gi<n&&el.dataset.fx==='fly'&&el.dataset.from&&slides[i].querySelector('#'+el.dataset.from);
    if(!animate||fly)el.style.transition='none';
    el.classList.toggle('pending',gi>=n);el.classList.toggle(el.dataset.fx,gi>=n);
    if(fly)flyIn(el,slides[i].querySelector('#'+el.dataset.from));
    if(!animate||fly){void el.offsetWidth;el.style.transition='';}
    if(el.dataset.fx==='type'){if(animate&&was&&gi<n)typeIn(el);else typeDone(el);}
  }));
  hlState(i,n,animate);
  const fx=slides[i]._fx;if(fx&&fx.step)try{fx.step(n,animate);}catch(e){console.error(e);}
}
// moves el from the centre of src to its own place, so a value looks like it travels there
function flyIn(el,src){
  const a=rectIn(src),b=rectIn(el);
  const dx=a.x+a.w/2-(b.x+b.w/2),dy=a.y+a.h/2-(b.y+b.h/2);
  const z=el.style.zIndex;el.style.zIndex=50;
  const k=Math.max(.12,Math.min(1,Math.max(a.w/b.w,a.h/b.h))),m=(1+k)/2;
  el.animate([{transformOrigin:'50% 50%',transform:'translate('+dx+'px,'+dy+'px) scale('+k+')',opacity:.3},{transformOrigin:'50% 50%',transform:'translate('+dx*.45+'px,'+(dy*.45-50)+'px) scale('+m+')',opacity:1,offset:.5},{transformOrigin:'50% 50%',transform:'none',opacity:1}],{duration:900,easing:'cubic-bezier(.4,0,.2,1)'}).onfinish=()=>{el.style.zIndex=z;};
}
// ---- highlights: typing, spotlight hole, mouse pointer (tools/HIGHLIGHT.md) ----
function textNodes(el){const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT),a=[];while(w.nextNode())a.push(w.currentNode);return a;}
function typeDone(el){if(el._tt){clearInterval(el._tt);el._tt=null;}if(el._orig)textNodes(el).forEach((t,k)=>t.nodeValue=el._orig[k]);}
function typeIn(el){
  typeDone(el);const ns=textNodes(el);el._orig=ns.map(t=>t.nodeValue);
  const total=el._orig.join('').length,ms=Math.max(12,Math.min(45,1100/Math.max(1,total)));
  ns.forEach(t=>t.nodeValue='');let k=0,j=0;
  el._tt=setInterval(()=>{while(k<ns.length&&j>=el._orig[k].length){k++;j=0;}if(k>=ns.length){typeDone(el);return;}j++;ns[k].nodeValue=el._orig[k].slice(0,j);},ms);
}
const CUR_SVG='<svg viewBox="0 0 22 30" width="40" height="56"><path d="M2,2 L2,24 L8,18 L12,28 L16,26 L12,16 L20,16 Z" fill="#1D2330" stroke="#fff" stroke-width="2" stroke-linejoin="round"/></svg>';
function hlParts(s){
  if(!s._spot){
    s._spot=document.createElement('div');s._spot.className='pl-spot';
    s._cur=document.createElement('div');s._cur.className='pl-cur';s._cur.innerHTML=CUR_SVG;
    s._rip=document.createElement('div');s._rip.className='pl-rip';
    s.append(s._spot,s._rip,s._cur);
  }
  return s;
}
function hlState(i,n,animate){
  const s=slides[i];let spot=null,cur=null,curNew=false;
  steps[i].forEach((g,gi)=>{if(gi>=n)return;g.forEach(el=>{const f=el.dataset.fx;
    if(f==='spot')spot=el;else if(f==='spot-off')spot=null;
    else if(f==='cursor'||f==='click'){cur=el;curNew=gi===n-1;}else if(f==='cursor-off')cur=null;});});
  if(!spot&&!cur&&!s._spot)return;
  hlParts(s);
  const sp=s._spot,cu=s._cur;
  const box=el=>(el.dataset.target&&s.querySelector('#'+el.dataset.target))||el;
  const still=x=>{x.style.transition='none';};
  const free=x=>{void x.offsetWidth;x.style.transition='';};
  if(spot){
    const r=rectIn(box(spot)),pad=+(spot.dataset.pad||12),rad=spot.dataset.r||'18px';
    sp.style.boxShadow='0 0 0 4px rgba(255,255,255,.92),0 0 0 4000px rgba(10,12,18,'+(spot.dataset.dim||.62)+')';
    const wasOn=sp.classList.contains('on');
    if(!animate||!wasOn)still(sp);
    Object.assign(sp.style,{left:(r.x-pad)+'px',top:(r.y-pad)+'px',width:(r.w+2*pad)+'px',height:(r.h+2*pad)+'px',borderRadius:rad});
    if(!animate||!wasOn)free(sp);
    if(!animate)still(sp);sp.classList.add('on');if(!animate)free(sp);
  }else{if(!animate)still(sp);sp.classList.remove('on');if(!animate)free(sp);}
  if(cur){
    const r=rectIn(box(cur)),x=r.x+r.w/2,y=r.y+r.h/2,wasOn=cu.classList.contains('on');
    if(animate&&!wasOn){still(cu);cu.style.left=(x+220)+'px';cu.style.top=(y+160)+'px';free(cu);}
    if(!animate)still(cu);
    cu.style.left=x+'px';cu.style.top=y+'px';cu.classList.add('on');
    if(!animate)free(cu);
    if(animate&&curNew&&cur.dataset.fx==='click'){clearTimeout(s._ripT);s._ripT=setTimeout(()=>{const rp=s._rip;rp.style.left=x+'px';rp.style.top=y+'px';rp.classList.remove('go');void rp.offsetWidth;rp.classList.add('go');},820);}
  }else{if(!animate)still(cu);cu.classList.remove('on');if(!animate)free(cu);}
}
function rectIn(el){const r=el.getBoundingClientRect(),S=stage.getBoundingClientRect(),k=stage._s;return{x:(r.left-S.left)/k,y:(r.top-S.top)/k,w:r.width/k,h:r.height/k};}
function topIds(sec){return [...sec.querySelectorAll('[id]')].filter(el=>!el.parentElement.closest('section [id]'));}
function show(n,dir){
  if(n<0||n>=slides.length)return;
  const a=slides[cur],b=slides[n];
  if(a._fx&&a._fx.leave&&n!==cur)try{a._fx.leave();}catch(e){console.error(e);}
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
  if(b._fx&&b._fx.enter)try{b._fx.enter();}catch(e){console.error(e);}
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
// slide scripts: see the note at the top of build_player.js
slides.forEach(s=>{
  const js=s.querySelector('script[type="text/slide-js"]');
  if(!js)return;
  try{s._fx=new Function('sec','api',js.textContent)(s,{animOn:()=>animOn,rectIn})||{};}catch(e){console.error(e);}
});
const start=Math.max(0,Math.min(slides.length-1,(parseInt(location.hash.slice(1))||1)-1));
slides.forEach((s,i)=>setBuild(i,0,false));
cur=start;step=animOn?0:steps[cur].length;seen[cur]=step;setBuild(cur,step,false);
$('pl-anim').textContent=animOn?'애니메이션 끄기':'애니메이션 켜기';$('pl-anim').classList.toggle('off',!animOn);
slides[cur].classList.add('on');update();
if(slides[cur]._fx&&slides[cur]._fx.enter)try{slides[cur]._fx.enter();}catch(e){console.error(e);}
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
