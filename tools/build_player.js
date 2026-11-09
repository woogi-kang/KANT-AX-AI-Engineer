// Builds one self-contained HTML file that plays the deck in a browser with its animations
// (build-ins and magic-move/fade transitions). Usage: node tools/build_player.js slides git-basics-slides.html
// Extras a slide can use, both ignored by check.js and export.js so the PDF shows the slide's plain layout:
// - data-build-in="fly order N" data-from="someId": the element flies in from where #someId is drawn.
// - highlights (see tools/HIGHLIGHT.md): data-build-in="draw order N" on an SVG draws its strokes like a pen;
//   "type order N" types the text in; "spot order N" on an empty box dims the slide except that box, and the
//   hole slides to the next "spot" box ("spot-off" clears it); "cursor order N" / "click order N" on an empty box
//   moves a mouse pointer there (click adds a ripple), "cursor-off" hides it. spot, cursor and click may name
//   data-target="someId" to use that element's box instead of their own.
// - more highlights (tools/HIGHLIGHT.md has the table, tools/highlight.py writes them):
//   entry kinds, hidden until their step: wipe (clip from the left), slam (big to normal), slide (data-dx/dy px),
//   stagger (children one by one, data-gap ms), count (number counts up), mark (span tint/strike fades in, stays
//   visible before), path (travels along svg path #data-path), morph (code tokens with data-m move from #data-from).
//   marker kinds, empty boxes that are never painted: lspot/lspot-off (veil the code box except data-ly/data-lh band),
//   run/run-off (green run band), zoom/zoom-off (camera into the box), blur/blur-off (blur all but #data-target),
//   text (#data-target text becomes data-text), pan (move #data-target by data-y), kenburns, and one-shot pulse,
//   grow, shine, shake on #data-target. Any build may carry data-delay (ms) or data-dimgroup (earlier ones dim).
//   Elements with data-pdf="hide" are hidden in the PDF and in check.js (the morph's first state).
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
#pl-bar{position:fixed;z-index:100;left:50%;bottom:16px;transform:translateX(-50%);display:flex;align-items:center;gap:2px;padding:6px;border-radius:14px;color:#E6E9EF;font-size:15px;background:rgba(14,17,23,.88);box-shadow:0 4px 18px rgba(0,0,0,.25);opacity:0;transition:opacity .2s}
body:hover #pl-bar,#pl-bar:focus-within,#pl-bar.keep{opacity:1}
#pl-bar button{position:relative;height:40px;min-width:40px;display:flex;align-items:center;justify-content:center;background:transparent;color:#E6E9EF;border:0;border-radius:10px;padding:0 8px;font:inherit;cursor:pointer}
#pl-bar button:hover{background:#2C3340}
#pl-bar button.on{background:#5A3BB8}
#pl-bar svg{display:block;width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
#pl-bar .sep{width:1px;height:24px;margin:0 6px;background:#3A4250}
#pl-count{font-variant-numeric:tabular-nums;white-space:nowrap;padding:0 10px!important}
#pl-go{display:none;width:64px;height:32px;margin:0 4px;background:#252B36;color:#E6E9EF;border:1px solid #5A6475;border-radius:8px;padding:0 8px;font:inherit;text-align:center}
#pl-bar.jump #pl-go{display:block}
#pl-bar.jump #pl-count{display:none}
#pl-anim .slash{display:none}
#pl-anim.on .slash{display:inline}
#pl-bar button[data-tip]:hover::after{content:attr(data-tip);position:absolute;bottom:calc(100% + 10px);left:50%;transform:translateX(-50%);white-space:nowrap;padding:6px 10px;border-radius:8px;background:#FFFFFF;color:#1D2330;font-size:14px;font-weight:500;box-shadow:0 2px 8px rgba(0,0,0,.25);pointer-events:none}
#pl-help{position:fixed;z-index:100;left:50%;bottom:76px;transform:translateX(-50%);display:none;padding:16px 20px;border-radius:12px;background:#FFFFFF;color:#1D2330;font-size:16px;line-height:1.5;box-shadow:0 6px 24px rgba(0,0,0,.3)}
#pl-help.show{display:block}
#pl-help table{border-collapse:collapse}
#pl-help td{padding:4px 10px;border:0}
#pl-help td:first-child{text-align:right;white-space:nowrap}
#pl-help kbd{display:inline-block;min-width:26px;padding:1px 7px;border:1px solid #C9CED8;border-bottom-width:2px;border-radius:6px;background:#F6F5F1;font:500 14px 'JetBrains Mono',monospace;text-align:center}
#pl-help p{margin:10px 0 0;font-size:14px;color:#6A7180}
#pl-notes{position:fixed;z-index:100;right:92px;bottom:80px;max-height:calc(100vh - 96px);width:min(460px,calc(100vw - 184px));display:none;flex-direction:column;border-radius:14px;background:#FFFFFF;color:#1D2330;box-shadow:0 8px 30px rgba(0,0,0,.3);overflow:hidden}
#pl-notes.show{display:flex}
#pl-notes .nin{flex:1;min-height:0;display:flex;flex-direction:column}
#pl-notes .nh{display:flex;align-items:flex-start;gap:10px;padding:16px 18px 14px;border-bottom:1px solid #ECEAE4;cursor:grab;touch-action:none;user-select:none}
#pl-notes .grip{flex:none;width:12px;height:20px;margin:1px -2px 0 -6px;fill:#B8BDC7}
#pl-notes .nh:hover .grip{fill:#6A7180}
#pl-notes.moving,#pl-notes.moving *{cursor:grabbing!important;user-select:none}
#pl-notes.moving{box-shadow:0 14px 44px rgba(0,0,0,.38)}
#pl-notes .rz{position:absolute;z-index:2;touch-action:none}
#pl-notes .rz[data-d=n]{left:14px;right:14px;top:0;height:7px;cursor:ns-resize}
#pl-notes .rz[data-d=s]{left:14px;right:14px;bottom:0;height:7px;cursor:ns-resize}
#pl-notes .rz[data-d=e]{top:14px;bottom:14px;right:0;width:7px;cursor:ew-resize}
#pl-notes .rz[data-d=w]{top:14px;bottom:14px;left:0;width:7px;cursor:ew-resize}
#pl-notes .rz[data-d=nw]{left:0;top:0;width:16px;height:16px;cursor:nwse-resize}
#pl-notes .rz[data-d=ne]{right:0;top:0;width:16px;height:16px;cursor:nesw-resize}
#pl-notes .rz[data-d=sw]{left:0;bottom:0;width:16px;height:16px;cursor:nesw-resize}
#pl-notes .rz[data-d=se]{right:0;bottom:0;width:22px;height:22px;cursor:nwse-resize;--g:#B8BDC7;background:linear-gradient(135deg,transparent 40%,var(--g) 40%,var(--g) 47%,transparent 47%,transparent 60%,var(--g) 60%,var(--g) 67%,transparent 67%) 0 0/16px 16px no-repeat}
#pl-notes .rz[data-d=se]:hover,#pl-notes.moving .rz[data-d=se]{--g:#6A7180}
#pl-notes .nh-t{flex:1;min-width:0}
#pl-notes .nh-k{font-size:13px;font-weight:500;color:#6A7180;letter-spacing:.02em}
#pl-notes .nh-h{margin-top:2px;font-size:19px;font-weight:700;line-height:1.35}
#pl-notes .nx{flex:none;width:32px;height:32px;border:0;border-radius:8px;background:transparent;color:#6A7180;font-size:22px;line-height:1;cursor:pointer}
#pl-notes .nx:hover{background:#F0EEE8;color:#1D2330}
#pl-notes .nb{flex:1;overflow:auto;padding:16px 18px 18px}
#pl-notes .lead{margin:0 0 14px;padding-left:12px;border-left:4px solid #5A3BB8;font-size:19px;font-weight:700;line-height:1.55;text-wrap:pretty}
#pl-notes ul{margin:0;padding:0;list-style:none}
#pl-notes li{position:relative;margin:0 0 10px;padding-left:18px;font-size:17px;line-height:1.65;text-wrap:pretty}
#pl-notes li::before{content:'';position:absolute;left:3px;top:.72em;width:6px;height:6px;border-radius:50%;background:#B8BDC7}
#pl-notes code{padding:1px 6px;border-radius:5px;background:#F1EEF9;color:#3F2A8C;font:500 .9em 'JetBrains Mono',monospace;white-space:nowrap}
#pl-notes .ch{padding:0 6px;border-radius:999px;background:#E8EEFB;color:#2459C9;font-weight:700}
#pl-notes .meta{margin-top:14px;padding-top:12px;border-top:1px dashed #E1DED6;font-size:14px;line-height:1.6;color:#6A7180}
#pl-notes .none{font-size:16px;color:#6A7180}
#pl-notes .nf{display:flex;gap:12px;justify-content:space-between;padding:10px 36px 10px 18px;border-top:1px solid #ECEAE4;background:#FAF9F6;font-size:13px;color:#6A7180}
#pl-notes .nf b{font-weight:500;color:#1D2330}
#pl-notes .nf span:last-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#pl-notes .nf span:first-child{flex:none;white-space:nowrap}
@media (max-width:640px){#pl-notes{left:12px;right:12px;width:auto}#pl-notes .rz,#pl-notes .grip{display:none}#pl-notes .nh{cursor:default}#pl-bar button{min-width:34px;padding:0 5px}#pl-bar .sep{margin:0 2px}}
[data-build-in^="spot"],[data-build-in^="cursor"],[data-build-in^="click"]{visibility:hidden}
[data-build-in^="draw"]{stroke-dasharray:1;transition:opacity .45s ease,stroke-dashoffset .7s cubic-bezier(.6,0,.3,1)}
.pending.draw{opacity:1!important;stroke-dashoffset:1}
.pl-spot{position:absolute;z-index:40;pointer-events:none;border-radius:18px;opacity:0;box-shadow:0 0 0 4px rgba(255,255,255,.92),0 0 0 4000px rgba(10,12,18,.62);transition:left .6s cubic-bezier(.65,0,.35,1),top .6s cubic-bezier(.65,0,.35,1),width .6s cubic-bezier(.65,0,.35,1),height .6s cubic-bezier(.65,0,.35,1),opacity .4s ease}
.pl-spot.on{opacity:1}
.pl-cur{position:absolute;z-index:45;width:40px;height:56px;margin:-4px 0 0 -6px;pointer-events:none;opacity:0;transition:left .8s cubic-bezier(.65,0,.35,1),top .8s cubic-bezier(.65,0,.35,1),opacity .3s ease}
.pl-cur.on{opacity:1}
.pl-rip{position:absolute;z-index:44;width:40px;height:40px;margin:-20px 0 0 -20px;border-radius:50%;border:5px solid #2459C9;opacity:0;pointer-events:none}
.pl-rip.go{animation:pl-rip .6s ease-out}
@keyframes pl-rip{0%{opacity:.9;transform:scale(.4)}100%{opacity:0;transform:scale(3)}}
#pl-stage [data-pdf="hide"]{visibility:inherit}
[data-build-in^="lspot"],[data-build-in^="run"],[data-build-in^="zoom"],[data-build-in^="blur"],[data-build-in^="text"],[data-build-in^="pan"],[data-build-in^="kenburns"],[data-build-in^="pulse"],[data-build-in^="grow"],[data-build-in^="shine"],[data-build-in^="shake"]{visibility:hidden}
[data-build-in^="wipe"]{clip-path:inset(0 0 0 0);transition:opacity .2s ease,clip-path .6s cubic-bezier(.65,0,.35,1)}
.pending.wipe{opacity:1!important;clip-path:inset(0 100% 0 0)}
[data-build-in^="slam"]{transition:opacity .25s ease,transform .5s cubic-bezier(.34,1.45,.64,1)}
.pending.slam{transform:scale(2.2)!important}
[data-build-in^="slide"]{transition:opacity .3s ease,transform .6s cubic-bezier(.16,1,.3,1)}
.pending.slide{transform:translate(var(--dx,0px),var(--dy,60px))!important}
.pending.stagger{opacity:1!important}
[data-build-in^="stagger"]>*{transition:opacity .35s ease,transform .4s cubic-bezier(.2,.7,.2,1)}
.pending.stagger>*{opacity:0;transform:translateY(18px)}
[data-build-in^="mark"]{transition:background-color .45s ease,color .45s ease,text-decoration-color .45s ease,box-shadow .45s ease}
.pending.mark{opacity:1!important;background-color:transparent!important;color:inherit!important;text-decoration-color:transparent!important;box-shadow:none!important}
[data-dimgroup]{transition:opacity .45s ease,transform .45s ease,filter .4s ease}
.pl-dim{filter:grayscale(1) opacity(.38)}
.pl-blurs>*{transition:opacity .45s ease,transform .45s ease,filter .5s ease}
.pl-bl{filter:blur(6px) opacity(.5)}
.pl-veil{position:absolute;z-index:30;pointer-events:none;opacity:.8;transition:left .45s cubic-bezier(.65,0,.35,1),top .45s cubic-bezier(.65,0,.35,1),width .45s cubic-bezier(.65,0,.35,1),height .45s cubic-bezier(.65,0,.35,1),opacity .35s ease}
.pl-lbar{position:absolute;z-index:31;width:7px;border-radius:4px;background:#2459C9;pointer-events:none;transition:top .45s cubic-bezier(.65,0,.35,1),height .45s cubic-bezier(.65,0,.35,1),left .45s,opacity .35s ease}
.pl-run{position:absolute;z-index:29;pointer-events:none;border-radius:8px;background:rgba(31,138,76,.17);box-shadow:inset 7px 0 0 #1F8A4C;transition:left .4s cubic-bezier(.65,0,.35,1),top .4s cubic-bezier(.65,0,.35,1),width .4s,height .4s,opacity .3s ease}
.pl-off{opacity:0!important}`;

const PLAYER_JS = `
const stage=document.getElementById('pl-stage');
const slides=[...stage.children];
const $=id=>document.getElementById(id);
let cur=0, step=0;
const HL_KINDS=['draw','type','spot','spot-off','cursor','click','cursor-off','wipe','slam','slide','stagger','count','mark','path','morph','lspot','lspot-off','run','run-off','zoom','zoom-off','blur','blur-off','text','pan','kenburns','pulse','grow','shine','shake'];
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
    if(kind==='slide'){el.style.setProperty('--dx',(el.dataset.dx||0)+'px');el.style.setProperty('--dy',(el.dataset.dy||60)+'px');}
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
    entryFx(el,animate&&was&&gi<n,gi<n,i);
    if(el.dataset.delay)el.style.transitionDelay=animate&&was&&gi<n?el.dataset.delay+'ms':'';
  }));
  hlState(i,n,animate);
  fxState(i,n,animate);
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
// ---- more highlights (tools/HIGHLIGHT.md): entry kinds that need script, then marker states ----
function entryFx(el,fresh,shown,i){
  const f=el.dataset.fx,s=slides[i];
  if(f==='stagger'){const gap=+(el.dataset.gap||70);[...el.children].forEach((c,k)=>{if(fresh){c.style.transitionDelay=(k*gap)+'ms';}else{c.style.transition='none';c.style.transitionDelay='';void c.offsetWidth;c.style.transition='';}});}
  else if(f==='count'){countFx(el,fresh,shown);}
  else if(f==='path'&&fresh){const p=s.querySelector('#'+el.dataset.path);if(p)pathFx(el,p);}
  else if(f==='morph'){const a=s.querySelector('#'+el.dataset.from);if(a){if(fresh)morphFx(a,el);a.style.visibility=shown?'hidden':'';}}
}
function countFx(el,fresh,shown){
  if(el._cnt===undefined){const tn=textNodes(el).find(t=>/\\d/.test(t.nodeValue));el._cntNode=tn;el._cnt=tn?tn.nodeValue:'';}
  const tn=el._cntNode;if(!tn)return;cancelAnimationFrame(el._raf);
  if(!fresh){tn.nodeValue=el._cnt;return;}
  const m=el._cnt.match(/[\\d,]*\\d(\\.\\d+)?/);if(!m){tn.nodeValue=el._cnt;return;}
  const to=parseFloat(m[0].replace(/,/g,'')),dec=(m[1]||'').length-1>0?(m[1].length-1):0,comma=m[0].includes(','),t0=performance.now(),ms=+(el.dataset.ms||1200);
  const fmt=v=>{let t=v.toFixed(dec);if(comma)t=Number(t).toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec});return el._cnt.slice(0,m.index)+t+el._cnt.slice(m.index+m[0].length);};
  const tick=now=>{const k=Math.min(1,(now-t0)/ms);tn.nodeValue=fmt(to*(1-Math.pow(1-k,3)));if(k<1)el._raf=requestAnimationFrame(tick);else tn.nodeValue=el._cnt;};
  tn.nodeValue=fmt(0);el._raf=requestAnimationFrame(tick);
}
function pathFx(el,p){
  const b=rectIn(el),cx=b.x+b.w/2,cy=b.y+b.h/2,L=p.getTotalLength(),S=stage.getBoundingClientRect(),k=stage._s,M=p.getScreenCTM(),fr=[];
  for(let j=0;j<=24;j++){const q=p.getPointAtLength(L*j/24),x=((M.a*q.x+M.c*q.y+M.e)-S.left)/k,y=((M.b*q.x+M.d*q.y+M.f)-S.top)/k;fr.push({transform:'translate('+(x-cx)+'px,'+(y-cy)+'px)',opacity:j?1:0});}
  fr[fr.length-1].transform='none';
  el.animate(fr,{duration:+(el.dataset.ms||1400),easing:'cubic-bezier(.45,0,.25,1)'});
}
function morphFx(a,b){
  [a,b].forEach(x=>x.querySelectorAll('[data-m]').forEach(t=>{if(getComputedStyle(t).display==='inline')t.style.display='inline-block';}));
  const from={};a.querySelectorAll('[data-m]').forEach(t=>from[t.dataset.m]=rectIn(t));
  a.style.visibility='hidden';
  b.style.transition='none';b.classList.remove('pending','morph');void b.offsetWidth;b.style.transition='';
  b.querySelectorAll('[data-m]').forEach(t=>{const p=from[t.dataset.m],q=rectIn(t);
    if(p)t.animate([{transform:'translate('+(p.x-q.x)+'px,'+(p.y-q.y)+'px)'},{transform:'none'}],{duration:850,easing:'cubic-bezier(.65,0,.35,1)'});
    else t.animate([{opacity:0},{opacity:0,offset:.55},{opacity:1}],{duration:850,easing:'ease'});});
  const g=a.cloneNode(true);g.removeAttribute('id');g.style.visibility='inherit';g.querySelectorAll('[id]').forEach(x=>x.removeAttribute('id'));
  g.querySelectorAll('[data-m]').forEach(t=>{if(b.querySelector('[data-m="'+t.dataset.m+'"]'))t.style.visibility='hidden';});
  a.parentNode.insertBefore(g,a);g.animate([{opacity:1},{opacity:0}],{duration:450,easing:'ease'}).onfinish=()=>g.remove();
}
function fxParts(s){
  if(!s._veil){
    s._veil=[0,1].map(()=>{const d=document.createElement('div');d.className='pl-veil pl-off';return d;});
    s._lbar=document.createElement('div');s._lbar.className='pl-lbar pl-off';
    s._run=document.createElement('div');s._run.className='pl-run pl-off';
    s.append(s._run,...s._veil,s._lbar);
  }
  return s;
}
function mbox(el){return{x:parseFloat(el.style.left)||0,y:parseFloat(el.style.top)||0,w:parseFloat(el.style.width)||0,h:parseFloat(el.style.height)||0};}
function fxState(i,n,animate){
  const s=slides[i];let ls=null,rn=null,zm=null,bl=null,last=null;const txt=new Map(),pan=new Map(),kb=new Map(),dims={};
  steps[i].forEach((g,gi)=>g.forEach(el=>{const f=el.dataset.fx,shown=gi<n;
    if(el.dataset.dimgroup&&shown){const d=dims[el.dataset.dimgroup]=dims[el.dataset.dimgroup]||{max:-1,els:[]};d.max=Math.max(d.max,gi);d.els.push([el,gi]);}
    if(el.dataset.dimgroup&&!shown)el.classList.remove('pl-dim');
    if(!shown)return;
    if(f==='lspot')ls=el;else if(f==='lspot-off')ls=null;
    else if(f==='run')rn=el;else if(f==='run-off')rn=null;
    else if(f==='zoom')zm=el;else if(f==='zoom-off')zm=null;
    else if(f==='blur')bl=el;else if(f==='blur-off')bl=null;
    else if(f==='text')txt.set(el.dataset.target,el);
    else if(f==='pan')pan.set(el.dataset.target,el);
    else if(f==='kenburns')kb.set(el.dataset.target,el);
    if(animate&&gi===n-1&&/^(pulse|grow|shine|shake|text)$/.test(f))(last=last||[]).push(el);
  }));
  Object.values(dims).forEach(d=>d.els.forEach(([el,gi])=>el.classList.toggle('pl-dim',gi<d.max)));
  const instant=(el,fn)=>{if(!animate){el.style.transition='none';fn();void el.offsetWidth;el.style.transition='';}else fn();};
  const any=ls||rn||s._veil;
  if(any){fxParts(s);
    if(ls){const b=mbox(ls),ly=+ls.dataset.ly,lh=+ls.dataset.lh,bg=ls.dataset.bg||'#FFFFFF',[v1,v2]=s._veil,wasOn=!v1.classList.contains('pl-off');
      const put=()=>{Object.assign(v1.style,{left:b.x+'px',top:b.y+'px',width:b.w+'px',height:Math.max(0,ly-b.y)+'px',background:bg});
        Object.assign(v2.style,{left:b.x+'px',top:(ly+lh)+'px',width:b.w+'px',height:Math.max(0,b.y+b.h-ly-lh)+'px',background:bg});
        Object.assign(s._lbar.style,{left:(b.x+8)+'px',top:(ly+6)+'px',height:Math.max(0,lh-12)+'px',background:ls.dataset.bar||'#2459C9'});};
      [v1,v2,s._lbar].forEach(x=>instant(x,()=>{}));
      if(!animate||!wasOn){[v1,v2,s._lbar].forEach(x=>{x.style.transition='none';});put();[v1,v2,s._lbar].forEach(x=>{void x.offsetWidth;x.style.transition='';});}else put();
      [v1,v2,s._lbar].forEach(x=>instant(x,()=>x.classList.remove('pl-off')));
    }else [...s._veil,s._lbar].forEach(x=>instant(x,()=>x.classList.add('pl-off')));
    if(rn){const b=mbox(rn),wasOn=!s._run.classList.contains('pl-off');
      const put=()=>Object.assign(s._run.style,{left:b.x+'px',top:b.y+'px',width:b.w+'px',height:b.h+'px'});
      if(!animate||!wasOn){s._run.style.transition='none';put();void s._run.offsetWidth;s._run.style.transition='';}else put();
      instant(s._run,()=>s._run.classList.remove('pl-off'));
    }else instant(s._run,()=>s._run.classList.add('pl-off'));
  }
  // blur everything on the slide except the part that holds the target
  if(bl||s.classList.contains('pl-blurs')){s.classList.add('pl-blurs');
    const t=bl&&s.querySelector('#'+bl.dataset.target);
    [...s.children].forEach(c=>{if(c.tagName==='ASIDE'||/^pl-/.test(c.className)||c.hasAttribute('data-build-in')&&/^(lspot|run|zoom|blur|text|pan|kenburns|pulse|grow|shine|shake|spot|cursor|click)/.test(c.getAttribute('data-build-in')))return;
      instant(c,()=>c.classList.toggle('pl-bl',!!t&&!c.contains(t)&&c!==t));});
    if(!bl&&!animate)s.classList.remove('pl-blurs');
  }
  // text values: the element keeps its last text in the HTML (for the PDF); data-start is what shows before any text step
  s.querySelectorAll('[data-start]').forEach(t=>{if(t._final===undefined)t._final=t.textContent;const m=txt.get(t.id);t.textContent=m?m.dataset.text:t.dataset.start;});
  pan.forEach((m,id)=>{const t=s.querySelector('#'+id);if(t){t.style.transition=animate?'transform '+(m.dataset.ms||2000)+'ms cubic-bezier(.65,0,.35,1)':'none';t.style.transform='translateY('+(m.dataset.y||0)+'px)';}});
  s.querySelectorAll('[data-panned]').forEach(t=>{if(!pan.has(t.id)){t.style.transition='none';t.style.transform='';}});
  pan.forEach((m,id)=>{const t=s.querySelector('#'+id);if(t)t.dataset.panned=1;});
  kb.forEach((m,id)=>{const t=s.querySelector('#'+id);if(t){t.style.transformOrigin=m.dataset.origin||'50% 50%';t.style.transition=animate?'transform '+(m.dataset.ms||6000)+'ms linear':'none';t.style.transform='scale('+(m.dataset.scale||1.12)+')';t.dataset.kb=1;}});
  s.querySelectorAll('[data-kb]').forEach(t=>{if(!kb.has(t.id)){t.style.transition='none';t.style.transform='';}});
  // camera: zoom the whole slide into the marker's box
  if(zm){const b=mbox(zm),pad=+(zm.dataset.pad||40),k=Math.min(1920/(b.w+2*pad),1080/(b.h+2*pad),+(zm.dataset.max||3));
    s.style.transformOrigin='0 0';s.style.transition=animate?'transform .9s cubic-bezier(.65,0,.35,1)':'none';
    s.style.transform='translate('+(960-(b.x+b.w/2)*k)+'px,'+(540-(b.y+b.h/2)*k)+'px) scale('+k+')';}
  else if(s.style.transform){s.style.transition=animate?'transform .9s cubic-bezier(.65,0,.35,1)':'none';s.style.transform='';}
  (last||[]).forEach(m=>{const t=s.querySelector('#'+m.dataset.target);if(!t)return;const f=m.dataset.fx;
    if(f==='pulse')t.animate([{transform:'scale(1)'},{transform:'scale(1.07)'},{transform:'scale(1)'},{transform:'scale(1.07)'},{transform:'scale(1)'}],{duration:900,easing:'ease-in-out'});
    else if(f==='grow')t.animate([{transform:'scale(1)'},{transform:'scale(1.2)',offset:.4},{transform:'scale(1)'}],{duration:800,easing:'cubic-bezier(.2,.7,.2,1)'});
    else if(f==='shake')t.animate([0,-14,14,-10,10,-5,0].map(x=>({transform:'translateX('+x+'px)'})),{duration:480,easing:'ease-out'});
    else if(f==='text')t.animate([{backgroundColor:'rgba(255,214,64,.6)'},{backgroundColor:'rgba(255,214,64,0)'}],{duration:900,easing:'ease-out'});
    else if(f==='shine'){const r=rectIn(t),g=document.createElement('div');Object.assign(g.style,{position:'absolute',left:r.x+'px',top:r.y+'px',width:r.w+'px',height:r.h+'px',overflow:'hidden',pointerEvents:'none',zIndex:35,borderRadius:getComputedStyle(t).borderRadius});
      g.innerHTML='<div style="position:absolute;top:0;left:-40%;width:30%;height:100%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.75),transparent);transform:skewX(-20deg)"></div>';s.appendChild(g);
      g.firstChild.animate([{left:'-40%'},{left:'120%'}],{duration:800,easing:'ease-in-out'}).onfinish=()=>g.remove();}
  });
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
// R or the bar button: put this slide back to its first screen, so its builds can be watched again with → or Space
function replay(){
  if(!steps[cur].length){toast('이 장은 애니메이션이 없어요');return;}
  if(!animOn){toast('애니메이션이 꺼져 있어요. A로 켜면 다시 볼 수 있어요',2600);return;}
  step=0;seen[cur]=0;setBuild(cur,0,false);
  slides[cur].animate([{opacity:.4},{opacity:1}],{duration:300,easing:'ease'});
  hideCopy();toast('처음 화면으로 돌렸어요. → 키를 누르면 다시 나와요',2400);update();
}
function go(n){n=Math.max(0,Math.min(slides.length-1,n));if(n!==cur)show(n,n<cur?-1:1);}
// ---- presenter notes: the aside's plain text laid out as a card ----
// first sentence = the point of the slide, the rest one sentence per line, notes about how outputs were made go to the bottom
const esc=t=>t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const META=/실제로 실행한 결과|셀 번호가|그 부분은 빼고 옮겼어요/;
function slideTitle(s){const h=s.querySelector('h1,h2,h3');return h?h.textContent.trim():'';}
function markNote(t){
  // code-like words (names with _ . ( ) =, ...Error, a lowercase word standing alone, not inside an English phrase such as New repository) become code chips, chapter numbers before 에서/의 become pills
  let out='',last=0;
  t.replace(/[A-Za-z_]\\w*(?:\\.\\w+)*(?:\\([^()\\s]*\\))?|\\[[^\\]\\s]*\\]/g,(w,i)=>{
    const alone=!/[A-Za-z]\\s*$/.test(t.slice(0,i))&&!/^\\s*[A-Za-z]/.test(t.slice(i+w.length));
    const code=/[_().=\\[\\]]/.test(w)||/Error$/.test(w)||(alone&&/^[a-z][a-z0-9]+$/.test(w));
    out+=esc(t.slice(last,i))+(code?'<code>'+esc(w)+'</code>':esc(w));last=i+w.length;return w;});
  out+=esc(t.slice(last));
  return out.replace(/(^|[^\\w>])(0[1-9]|[12][0-9])(?=(에서|의|챕터)[\\s,.])/g,'$1<span class="ch">$2</span>');
}
function renderNotes(text){
  const t=text.replace(/\\s+/g,' ').trim();
  const ss=t?t.split(/(?<=[.?!])\\s+(?=\\S)/):[];
  const main=ss.filter(x=>!META.test(x)),meta=ss.filter(x=>META.test(x));
  const n=steps[cur].length,title=slideTitle(slides[cur]),nt=cur+1<slides.length?slideTitle(slides[cur+1]):'';
  const body=main.length?'<p class="lead">'+markNote(main[0])+'</p><ul>'+main.slice(1).map(x=>'<li>'+markNote(x)+'</li>').join('')+'</ul>'+(meta.length?'<div class="meta">'+meta.map(markNote).join(' ')+'</div>':'')
    :'<p class="none">이 장은 노트가 없어요.</p>';
  $('pl-notes').querySelector('.nin').innerHTML='<div class="nh" title="끌어서 옮기기, 두 번 누르면 처음 자리"><svg class="grip" viewBox="0 0 12 20"><circle cx="3" cy="4" r="1.6"/><circle cx="9" cy="4" r="1.6"/><circle cx="3" cy="10" r="1.6"/><circle cx="9" cy="10" r="1.6"/><circle cx="3" cy="16" r="1.6"/><circle cx="9" cy="16" r="1.6"/></svg><div class="nh-t"><div class="nh-k">발표자 노트 · '+(cur+1)+' / '+slides.length+'</div><div class="nh-h">'+esc(title)+'</div></div><button class="nx" aria-label="노트 닫기">×</button></div>'
    +'<div class="nb">'+body+'</div>'
    +'<div class="nf"><span>'+(n?'애니메이션 <b>'+step+' / '+n+'</b>':'애니메이션 없음')+'</span><span>'+(nt?'다음 장 <b>'+esc(nt)+'</b>':'마지막 장')+'</span></div>';
  $('pl-notes').querySelector('.nx').onclick=()=>notes(false);
}
function notes(show){const el=$('pl-notes');el.classList.toggle('show',show===undefined?!el.classList.contains('show'):show);$('pl-nb').classList.toggle('on',el.classList.contains('show'));placeNotes();}
// The notes card works like a window: drag the top strip to move it, drag an edge or corner to resize it,
// double-click the top strip to put it back. Position and size are kept in localStorage (slides-notes-box).
// On phone width the card keeps its fixed layout.
const NBOX='slides-notes-box',NMIN_W=300,NMIN_H=180,NGAP=8;
let nbox=null;try{nbox=JSON.parse(localStorage.getItem(NBOX));}catch(e){}
const nwin=()=>innerWidth>640;
function placeNotes(){
  const el=$('pl-notes');
  if(!nbox||!nwin()){el.style.cssText='';return;}
  const vw=innerWidth,vh=innerHeight;
  const w=Math.max(NMIN_W,Math.min(nbox.w,vw-2*NGAP));
  const h=nbox.h?Math.max(NMIN_H,Math.min(nbox.h,vh-2*NGAP)):0;
  el.style.right=el.style.bottom='auto';el.style.width=w+'px';el.style.height=h?h+'px':'';
  const left=Math.max(NGAP,Math.min(nbox.x,vw-w-NGAP));
  el.style.left=left+'px';
  const oh=h||Math.min(el.offsetHeight||NMIN_H,vh-2*NGAP);
  const top=Math.max(NGAP,Math.min(nbox.y,vh-Math.min(oh,vh-2*NGAP)-NGAP));
  el.style.top=top+'px';el.style.maxHeight=h?'none':(vh-top-NGAP)+'px';
}
function saveNotes(){try{nbox?localStorage.setItem(NBOX,JSON.stringify(nbox)):localStorage.removeItem(NBOX);}catch(e){}}
let ndrag=null,nlast=0;
$('pl-notes').addEventListener('pointerdown',e=>{
  if(!nwin()||e.button!==0||e.target.closest('.nx'))return;
  const rz=e.target.closest('.rz'),el=$('pl-notes');
  if(!rz&&!e.target.closest('.nh'))return;
  e.preventDefault();
  const r=el.getBoundingClientRect();
  // double-click on the top strip puts the card back where it started
  const now=Date.now();
  if(!rz&&now-nlast<350){nlast=0;nbox=null;saveNotes();placeNotes();toast('노트 창을 처음 자리로 돌렸어요');return;}
  nlast=rz?0:now;
  ndrag={d:rz?rz.dataset.d:'move',x:e.clientX,y:e.clientY,r,h:nbox&&nbox.h?r.height:0};
  el.setPointerCapture(e.pointerId);el.classList.add('moving');
});
$('pl-notes').addEventListener('pointermove',e=>{
  if(!ndrag)return;
  const d=ndrag.d,dx=e.clientX-ndrag.x,dy=e.clientY-ndrag.y,r=ndrag.r;
  let x=r.left,y=r.top,w=r.width,h=ndrag.h;
  if(d==='move'){x+=dx;y+=dy;}
  else{
    if(d.includes('e'))w=Math.max(NMIN_W,r.width+dx);
    if(d.includes('w')){w=Math.max(NMIN_W,r.width-dx);x=r.right-w;}
    if(d.includes('s'))h=Math.max(NMIN_H,r.height+dy);
    if(d.includes('n')){h=Math.max(NMIN_H,r.height-dy);y=r.bottom-h;}
  }
  nbox={x,y,w,h};placeNotes();
  const el=$('pl-notes');nbox.x=parseFloat(el.style.left);nbox.y=parseFloat(el.style.top);nbox.w=el.offsetWidth;
});
function endDrag(){if(!ndrag)return;ndrag=null;$('pl-notes').classList.remove('moving');saveNotes();}
$('pl-notes').addEventListener('pointerup',endDrag);
$('pl-notes').addEventListener('pointercancel',endDrag);
function update(){
  $('pl-count').textContent=(cur+1)+' / '+slides.length;
  const aside=slides[cur].querySelector('aside');
  renderNotes(aside?aside.textContent:'');
  history.replaceState(null,'','#'+(cur+1));
}
let toastT;
function toast(msg,ms){const t=$('pl-toast');clearTimeout(toastT);if(!msg){t.classList.remove('show');return;}t.textContent=msg;t.classList.add('show');toastT=setTimeout(()=>t.classList.remove('show'),ms||1800);}
function setAnim(on){
  animOn=on;try{localStorage.setItem('slides-anim',on?'on':'off');}catch(e){}
  animBtn();
  if(!on){step=steps[cur].length;seen[cur]=step;setBuild(cur,step,true);}
  toast(on?'애니메이션을 켰어요':'애니메이션을 껐어요. 모든 장을 다 펼쳐서 보여 줘요');update();
}
function animBtn(){const b=$('pl-anim');b.classList.toggle('on',!animOn);b.dataset.tip=animOn?'애니메이션 끄기 (A)':'애니메이션 켜기 (A)';b.setAttribute('aria-label',b.dataset.tip);}
function help(show){const h=$('pl-help');h.classList.toggle('show',show===undefined?!h.classList.contains('show'):show);$('pl-bar').classList.toggle('keep',h.classList.contains('show'));}
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
  if(e.key==='Escape'){setJump('');help(false);return;}
  if(e.key==='?'){help();return;}
  if(['ArrowRight','ArrowDown','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();next();}
  else if(['ArrowLeft','ArrowUp','PageUp','Backspace'].includes(e.key)){e.preventDefault();prev();}
  else if(e.key==='Home')go(0);
  else if(e.key==='End')go(slides.length-1);
  else if(e.key==='n'||e.key==='N')notes();
  else if(e.key==='a'||e.key==='A')setAnim(!animOn);
  else if(e.key==='r'||e.key==='R')replay();
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
  const onUi=t.closest&&t.closest('#pl-bar,#pl-notes,#pl-help,#pl-copy,.hint');
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
addEventListener('resize',()=>{hideCopy();placeNotes();});
$('pl-nb').onclick=()=>notes();
$('pl-fs').onclick=fullscreen;
$('pl-anim').onclick=()=>setAnim(!animOn);
$('pl-replay').onclick=replay;
$('pl-help-btn').onclick=()=>help();
// the page counter turns into a page-number box when clicked
$('pl-count').onclick=()=>{$('pl-bar').classList.add('jump');$('pl-go').focus();};
$('pl-go').addEventListener('blur',()=>{$('pl-go').value='';$('pl-bar').classList.remove('jump');});
$('pl-go').addEventListener('keydown',e=>{
  if(e.key==='Enter'){const n=parseInt(e.target.value);e.target.blur();if(n>0)go(n-1);}
  else if(e.key==='Escape'){e.target.blur();}
});
let tx=null;addEventListener('touchstart',e=>{tx=e.target.closest&&e.target.closest('#pl-notes')?null:e.touches[0].clientX;});addEventListener('touchend',e=>{if(tx===null)return;const d=e.changedTouches[0].clientX-tx;if(Math.abs(d)>40)(d<0?next:prev)();tx=null;});
// slide scripts: see the note at the top of build_player.js
slides.forEach(s=>{
  const js=s.querySelector('script[type="text/slide-js"]');
  if(!js)return;
  try{s._fx=new Function('sec','api',js.textContent)(s,{animOn:()=>animOn,rectIn})||{};}catch(e){console.error(e);}
});
const start=Math.max(0,Math.min(slides.length-1,(parseInt(location.hash.slice(1))||1)-1));
slides.forEach((s,i)=>setBuild(i,0,false));
cur=start;step=animOn?0:steps[cur].length;seen[cur]=step;setBuild(cur,step,false);
animBtn();
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
<div id="pl-notes"><div class="nin"></div><i class="rz" data-d="n"></i><i class="rz" data-d="s"></i><i class="rz" data-d="e"></i><i class="rz" data-d="w"></i><i class="rz" data-d="nw"></i><i class="rz" data-d="ne"></i><i class="rz" data-d="sw"></i><i class="rz" data-d="se"></i></div>
<div id="pl-bar"><button id="pl-prev" data-tip="이전 (←)" aria-label="이전"><svg viewBox="0 0 24 24"><polyline points="15,5 8,12 15,19"/></svg></button><button id="pl-count" data-tip="눌러서 쪽 번호로 가기" aria-label="쪽 번호로 가기"></button><input id="pl-go" inputmode="numeric" placeholder="쪽" aria-label="쪽 번호"><button id="pl-next" data-tip="다음 (→)" aria-label="다음"><svg viewBox="0 0 24 24"><polyline points="9,5 16,12 9,19"/></svg></button><span class="sep"></span><button id="pl-replay" data-tip="다시 보기 (R)" aria-label="다시 보기"><svg viewBox="0 0 24 24"><path d="M3.5 12a8.5 8.5 0 1 0 2.6-6.1"/><polyline points="3.5,3.5 3.5,8.5 8.5,8.5"/></svg></button><button id="pl-anim" data-tip="애니메이션 끄기 (A)" aria-label="애니메이션 끄기"><svg viewBox="0 0 24 24"><path d="M12 3.5l1.9 5.1 5.1 1.9-5.1 1.9L12 17.5l-1.9-5.1-5.1-1.9 5.1-1.9z"/><path d="M18.5 16v4M16.5 18h4"/><line class="slash" x1="4" y1="4" x2="20" y2="20"/></svg></button><button id="pl-nb" data-tip="발표자 노트 (N)" aria-label="발표자 노트"><svg viewBox="0 0 24 24"><rect x="5" y="3.5" width="14" height="17" rx="2"/><path d="M9 8.5h6M9 12h6M9 15.5h4"/></svg></button><button id="pl-fs" data-tip="전체 화면 (F)" aria-label="전체 화면"><svg viewBox="0 0 24 24"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg></button><button id="pl-help-btn" data-tip="단축키 (?)" aria-label="단축키"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5"/><path d="M9.6 9.6a2.5 2.5 0 1 1 3.4 2.3c-.6.3-1 .8-1 1.5v.4"/><line x1="12" y1="17" x2="12" y2="17.1"/></svg></button></div>
<div id="pl-help"><table><tr><td><kbd>→</kbd> <kbd>Space</kbd></td><td>다음 (애니메이션을 하나씩)</td></tr><tr><td><kbd>←</kbd></td><td>이전</td></tr><tr><td>숫자 뒤 <kbd>Enter</kbd></td><td>그 장으로 가기</td></tr><tr><td><kbd>R</kbd></td><td>지금 장 애니메이션 다시 보기</td></tr><tr><td><kbd>A</kbd></td><td>애니메이션 끄고 켜기</td></tr><tr><td><kbd>N</kbd></td><td>발표자 노트</td></tr><tr><td><kbd>F</kbd></td><td>전체 화면</td></tr><tr><td><kbd>?</kbd></td><td>이 안내 열고 닫기</td></tr></table><p>화면 양옆 화살표 버튼은 남은 애니메이션을 건너뛰고 바로 넘겨요.<br>노트 카드는 위쪽을 끌면 옮겨지고, 가장자리를 끌면 크기가 바뀌어요.</p></div>
<script>${PLAYER_JS}</script>
</body></html>`;
  fs.writeFileSync(out, html);
  console.log(`${deck.order.length} slides -> ${out} (${(html.length / 1024).toFixed(0)} KB)`);
})();
