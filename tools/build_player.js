// Builds one self-contained HTML file that plays the deck in a browser with its animations
// (build-ins and magic-move/fade transitions). Usage: node tools/build_player.js slides git-basics-slides.html
const fs = require('fs');
const { renderDeck } = require('./deckrender');
const [dir, out] = process.argv.slice(2);

const PLAYER_CSS = `html,body{margin:0;height:100%;background:#0E1117;overflow:hidden;font-family:'Noto Sans KR',Arial,sans-serif}
#stage{position:absolute;left:50%;top:50%;width:1920px;height:1080px;transform-origin:center center;overflow:hidden;background:#F6F5F1}
#stage>section{position:absolute;left:0;top:0;visibility:hidden}
#stage>section.on{visibility:visible}
[data-build-in]{transition:opacity .45s ease,transform .45s ease}
.pending{opacity:0!important}
.pending.rise{transform:translateY(40px)!important}
.pending.pop{transform:scale(.85)!important}
#bar{position:fixed;left:0;right:0;bottom:0;display:flex;align-items:center;gap:16px;padding:8px 16px;color:#C9CED8;font-size:14px;background:rgba(14,17,23,.85);opacity:0;transition:opacity .2s}
body:hover #bar,#bar:focus-within{opacity:1}
#bar button{background:#252B36;color:#E6E9EF;border:0;border-radius:6px;padding:6px 12px;font:inherit;cursor:pointer}
#bar .grow{flex:1}
#notes{position:fixed;left:16px;right:16px;bottom:52px;max-height:30vh;overflow:auto;padding:16px 20px;border-radius:10px;background:rgba(255,255,255,.96);color:#1D2330;font-size:18px;line-height:1.6;display:none}
#notes.show{display:block}`;

const PLAYER_JS = `
const stage=document.getElementById('stage');
const slides=[...stage.children];
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
  setBuild(n,dir<0?steps[n].length:0,false);
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
  cur=n;step=dir<0?steps[n].length:0;
  update();
}
function next(){if(step<steps[cur].length){step++;setBuild(cur,step,true);update();}else show(cur+1,1);}
function prev(){show(cur-1,-1);}
function update(){
  document.getElementById('count').textContent=(cur+1)+' / '+slides.length;
  const aside=slides[cur].querySelector('aside');
  document.getElementById('notes').textContent=aside?aside.textContent:'';
  history.replaceState(null,'','#'+(cur+1));
}
addEventListener('keydown',e=>{
  if(['ArrowRight','ArrowDown','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();next();}
  else if(['ArrowLeft','ArrowUp','PageUp','Backspace'].includes(e.key)){e.preventDefault();prev();}
  else if(e.key==='Home')show(0,1);
  else if(e.key==='End')show(slides.length-1,1);
  else if(e.key==='n'||e.key==='N')document.getElementById('notes').classList.toggle('show');
  else if(e.key==='f'||e.key==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();}
});
stage.addEventListener('click',e=>{(e.clientX<innerWidth/3)?prev():next();});
document.getElementById('prev').onclick=prev;document.getElementById('next').onclick=next;
document.getElementById('nb').onclick=()=>document.getElementById('notes').classList.toggle('show');
document.getElementById('fs').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
let tx=null;addEventListener('touchstart',e=>tx=e.touches[0].clientX);addEventListener('touchend',e=>{if(tx===null)return;const d=e.changedTouches[0].clientX-tx;if(Math.abs(d)>40)(d<0?next:prev)();tx=null;});
const start=Math.max(0,Math.min(slides.length-1,(parseInt(location.hash.slice(1))||1)-1));
slides.forEach((s,i)=>setBuild(i,0,false));
cur=start;slides[cur].classList.add('on');update();
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
<div id="stage">
${sections}
</div>
<div id="notes"></div>
<div id="bar"><button id="prev">이전</button><button id="next">다음</button><span id="count"></span><span class="grow"></span><span>→ 다음 · ← 이전 · N 발표자 노트 · F 전체 화면</span><button id="nb">노트</button><button id="fs">전체 화면</button></div>
<script>${PLAYER_JS}</script>
</body></html>`;
  fs.writeFileSync(out, html);
  console.log(`${deck.order.length} slides -> ${out} (${(html.length / 1024).toFixed(0)} KB)`);
})();
