// 시안 v8 · 역할별 여정과 시작점 진단. 질문 세 개에 답하면 어느 길의 몇 번째 이정표부터 보면 되는지 알려 줘요(저장하지 않아요).
import { i, esc, write } from "../lib.mjs";
import { JOURNEYS, MILE, QUIZ, CHANGES, FOOT_NEW, COPY, searchKit, DLG_CSS, items, html, deck, pdf, md } from "../new/content.mjs";

const css = `:root{--bg:#FBFAF7;--card:#FFFFFF;--ink:#1B1D22;--sub:#5D626D;--mute:#8C909A;--line:#E3E0D8;--ac:#2459C9;--ac-s:#EAF0FC}
[data-theme=dark]{--bg:#14161A;--card:#1C1F24;--ink:#ECEDEF;--sub:#A5AAB4;--mute:#7D828D;--line:#2E323A;--ac:#86A8F2;--ac-s:#1E2840}
body{background:var(--bg);color:var(--ink);font-size:16px;line-height:1.6}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px}
.hd .wrap{display:flex;align-items:center;gap:28px;height:68px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:17px;white-space:nowrap}
.bm{display:flex;gap:3px}.bm i{display:block;width:8px;height:22px;border-radius:4px}.bm i:nth-child(1){background:#2459C9}.bm i:nth-child(2){background:#1F8A4C;height:16px;margin-top:6px}.bm i:nth-child(3){background:#B26A00;height:10px;margin-top:12px}
.nav{display:flex;gap:6px}.nav a{padding:7px 12px;border-radius:99px;font-weight:600;color:var(--sub)}.nav a[aria-current]{background:var(--ink);color:var(--bg)}
.tools{margin-left:auto;display:flex;gap:8px}.ib{height:38px;min-width:38px;padding:0 10px;display:flex;gap:8px;align-items:center;justify-content:center;border:1px solid var(--line);border-radius:99px;background:var(--card);cursor:pointer;color:var(--sub)}
.ib kbd{font-size:12px}[data-theme=light] .ib .moon-i,[data-theme=dark] .ib .sun-i{display:none}
.hero{padding:40px 0 56px}.hero .wrap{display:grid;grid-template-columns:1fr 520px;gap:56px;align-items:center}
.hero h1{font-size:46px;line-height:1.22;letter-spacing:-.03em}.hero p{color:var(--sub);font-size:18px;margin-top:16px;max-width:520px}
.facts{display:flex;gap:18px;flex-wrap:wrap;margin-top:22px;color:var(--sub);font-size:15px}.facts span{display:flex;align-items:center;gap:6px}.facts .i{width:16px;height:16px;color:var(--ink)}
.quiz{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:26px;box-shadow:0 1px 0 var(--line)}
.quiz h2{font-size:20px;letter-spacing:-.01em;display:flex;gap:8px;align-items:center}.quiz h2 .i{color:var(--ac)}
.q{margin-top:18px;border:0;padding:0}.q legend{font-weight:700;font-size:15px;margin-bottom:8px;padding:0}
.opts{display:flex;flex-wrap:wrap;gap:8px}.opts label{cursor:pointer}.opts input{position:absolute;opacity:0;pointer-events:none}
.opts span{display:inline-block;padding:7px 14px;border:1.5px solid var(--line);border-radius:99px;font-size:15px}.opts input:checked+span{border-color:var(--ink);background:var(--ink);color:var(--bg)}.opts input:focus-visible+span{outline:2px solid var(--ac);outline-offset:2px}
.rec{margin-top:22px;border-radius:14px;padding:16px 18px;background:var(--ac-s);display:flex;gap:14px;align-items:center}
.rec .st{width:40px;height:40px;border-radius:50%;flex:none;display:grid;place-items:center;color:#fff;font-weight:800;background:var(--c,#2459C9)}
.rec small{color:var(--sub);font-size:13px;display:block}.rec b{font-size:17px;display:block;line-height:1.35}.rec a{margin-left:auto;flex:none;display:flex;align-items:center;gap:4px;font-weight:700;color:var(--ac)}
.quiz .note{font-size:13px;color:var(--mute);margin-top:10px}
.sec{padding:56px 0;border-top:1px solid var(--line)}.sec h2{font-size:30px;letter-spacing:-.02em}.sec .sub{color:var(--sub);margin-top:6px}
.lane{margin-top:36px;background:var(--card);border:1px solid var(--line);border-radius:20px;padding:24px 28px 28px}
.lane-h{display:flex;align-items:center;gap:12px}.lane-h .ico{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;color:#fff;background:var(--c)}
.lane-h b{font-size:19px}.lane-h small{margin-left:auto;color:var(--sub);font-size:14px}
.line{list-style:none;padding:0;margin:26px 0 0;display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));position:relative}
.line::before{content:"";position:absolute;left:12px;right:12px;top:11px;height:6px;border-radius:3px;background:var(--c)}
.line li{position:relative;padding:40px 14px 0 0}
.line li::before{content:"";position:absolute;left:0;top:0;width:28px;height:28px;border-radius:50%;background:var(--card);border:6px solid var(--c);box-sizing:border-box}
.line li.soon::before{border-color:var(--line);border-width:5px}
.line .k{font-size:13px;font-weight:700;color:var(--c)}.line b{display:block;font-size:16px;line-height:1.35;margin-top:2px}.line p{font-size:14px;color:var(--sub);margin-top:4px;line-height:1.5}
.line .r{display:inline-block;margin-top:8px;font-size:13px;color:var(--sub)}.line a:hover b{color:var(--ac)}
.same{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:28px}.same div{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px}.same .i{color:var(--ac);width:22px;height:22px}.same b{display:block;margin-top:10px;font-size:17px}.same p{color:var(--sub);font-size:15px;margin-top:4px}
.chg{list-style:none;padding:0;margin:20px 0 0;display:flex;flex-direction:column;gap:8px}.chg li{display:flex;gap:16px}.chg time{color:var(--mute);width:96px;flex:none;font-size:14px;padding-top:1px}
.ft{padding:32px 0 44px;color:var(--sub);font-size:14px;border-top:1px solid var(--line)}.ft .wrap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
/* 이정표 화면 */
.band{background:var(--card);border-bottom:1px solid var(--line)}.band .wrap{padding-top:22px;padding-bottom:26px}
.back{display:inline-flex;gap:6px;align-items:center;color:var(--sub);font-size:14px}.back .i{width:15px;height:15px}
.trk{list-style:none;padding:0;margin:18px 0 0;display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));position:relative}
.trk::before{content:"";position:absolute;left:13px;right:calc(100% / var(--n) - 13px);top:17px;height:5px;background:var(--c)}
.trk li{position:relative;min-width:0;padding-right:8px}.trk .s{position:relative;margin-top:7px;width:26px;height:26px;border-radius:50%;border:5px solid var(--c);background:var(--card);display:grid;place-items:center;font-size:0}
.trk .on .s{margin-top:0;margin-left:-7px;width:40px;height:40px;background:var(--c);color:#fff;font-size:16px;font-weight:800;border:0}
.trk .l{display:block;margin-top:8px;font-size:13px;color:var(--sub);line-height:1.4}.trk .on .l{color:var(--ink);font-weight:800;margin-top:1px}
.mh{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:56px;padding:40px 0 72px}
.who{font-size:15px;color:var(--c);font-weight:700}.mh h1{font-size:40px;letter-spacing:-.025em;line-height:1.22;margin-top:4px}
.can{font-size:21px;margin-top:14px;line-height:1.5}
.blk{margin-top:44px}.blk h2{font-size:22px;letter-spacing:-.01em;margin-bottom:14px;display:flex;align-items:center;gap:10px}.blk h2 .i{width:22px;height:22px;color:var(--ac)}
.task{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:22px 24px}.task b{font-size:18px}
.task ol{margin:12px 0 0;padding:0;list-style:none;counter-reset:s}.task ol li{counter-increment:s;display:flex;gap:12px;padding:8px 0;border-top:1px dashed var(--line)}.task ol li:first-child{border-top:0}
.task ol li::before{content:counter(s);width:26px;height:26px;border-radius:50%;background:var(--ink);color:var(--bg);font-size:13px;font-weight:800;display:grid;place-items:center;flex:none}
details{margin-top:12px;border-top:1px solid var(--line);padding-top:12px}summary{cursor:pointer;font-weight:700;color:var(--ac);list-style:none;display:flex;gap:6px;align-items:center}summary::-webkit-details-marker{display:none}summary .i{width:16px;height:16px}
details ul{margin:10px 0 0;padding-left:20px;color:var(--sub)}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.cd{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;display:flex;flex-direction:column}.cd img{width:100%;aspect-ratio:16/9;object-fit:cover;border-bottom:1px solid var(--line)}
.cd div{padding:12px 14px 14px;flex:1;display:flex;flex-direction:column}.cd b{line-height:1.4}.cd p{font-size:14px;color:var(--sub);margin-top:4px;flex:1}
.cd nav{display:flex;gap:14px;margin-top:10px;font-size:14px;font-weight:700}.cd nav a{display:flex;gap:5px;align-items:center;color:var(--ac)}.cd nav .i{width:15px;height:15px}
.self{list-style:none;padding:0;margin:0}.self li{display:flex;gap:10px;padding:12px 0;border-bottom:1px solid var(--line)}.self .i{color:var(--mute);margin-top:3px}
.aside{align-self:start;position:sticky;top:20px;display:flex;flex-direction:column;gap:16px}
.box{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:20px}.box h3{font-size:14px;color:var(--sub);font-weight:600}
.box .nx{display:flex;align-items:center;gap:12px;margin-top:10px}.box .nx .s{width:34px;height:34px;border-radius:50%;border:5px solid var(--c);flex:none}.box .nx b{display:block;font-size:17px;line-height:1.35}.box .nx small{color:var(--sub)}
.box ul{list-style:none;padding:0;margin:10px 0 0}.box li{display:flex;gap:8px;align-items:center;padding:6px 0;font-size:15px}.box li .i{width:16px;height:16px;color:var(--sub)}
${DLG_CSS({ scrim: "rgba(20,22,26,.4)", bg: "var(--card)", ink: "var(--ink)", line: "var(--line)", r: "16px", sub: "var(--sub)", hover: "var(--bg)" })}
@media (max-width:1100px){.hero .wrap{grid-template-columns:1fr;gap:32px}.mh{grid-template-columns:1fr}.aside{position:static}}
@media (max-width:860px){.line{grid-template-columns:1fr;gap:18px;margin-top:20px}.line::before{left:11px;right:auto;top:12px;bottom:12px;width:6px;height:auto}.line li{padding:0 0 0 44px}
.same{grid-template-columns:1fr}.trk .l{display:none}}
@media (max-width:640px){.wrap{padding:0 16px}.nav{display:none}.ib kbd{display:none}.hero{padding:20px 0 40px}.hero h1{font-size:31px}.hero p{font-size:16px}.quiz{padding:20px}.lane{padding:20px}
.lane-h small{display:none}.sec h2{font-size:25px}.mh{padding:28px 0 56px}.mh h1{font-size:30px}.can{font-size:18px}.cards{grid-template-columns:1fr}.rec{flex-wrap:wrap}.rec a{margin-left:54px}}`;

const header = (cur) => `<header class="hd"><div class="wrap"><a class="brand" href="home.html"><span class="bm"><i></i><i></i><i></i></span>풀스택 AI/AX 여정</a>
<nav class="nav" aria-label="메뉴">${[["여정", "home.html"], ["가이드라인", "#"], ["꿀팁", "#"], ["소식", "#"]].map(([t, h]) => `<a href="${h}"${t === cur ? ' aria-current="page"' : ""}>${t}</a>`).join("")}</nav>
<div class="tools"><button class="ib" data-search aria-label="찾기">${i("search")}<kbd>/</kbd></button><button class="ib" data-theme-toggle aria-label="화면 밝기 바꾸기">${i("moon", "i moon-i")}${i("sun", "i sun-i")}</button></div></div></header>`;
const footer = `<footer class="ft"><div class="wrap"><span>${FOOT_NEW}</span><span>${COPY}</span></div></footer>`;
const kit = searchKit(items, "milestone.html");

const J = JSON.stringify(JOURNEYS.map((j) => ({ id: j.id, c: j.color, who: j.who, m: j.miles.map((m) => m[0]) })));
const quizJs = `<script>(()=>{const J=${J};const f=document.querySelector('[data-quiz]');const out=f.querySelector('.rec');
function pick(){const v=n=>(f.querySelector('input[name='+n+']:checked')||{}).value;const who=v('q0'),lv=+v('q1'),want=v('q2');
const j=J.find(x=>x.id===who);let k=0;
if(who==='new'){k=[0,1,3][lv];if(want==='build'&&lv===2)k=4;if(want==='data'&&lv>0)k=3}
else if(who==='ax'){k=want==='data'?2:want==='build'?3:(lv?1:0)}
else{k=lv===2?1:0}
out.style.setProperty('--c',j.c);out.querySelector('.st').textContent=k+1;out.querySelector('small').textContent=j.who+' · '+(k+1)+'번째 이정표';out.querySelector('b').textContent=j.m[k]+'부터 시작해 보세요'}
f.addEventListener('change',pick);pick()})()</script>`;

const lane = (j) => `<div class="lane" style="--c:${j.color}"><div class="lane-h"><span class="ico">${i(j.icon)}</span><b>${esc(j.who)}</b><small>이정표 ${j.miles.length}개</small></div>
<ol class="line" style="--n:${j.miles.length}">${j.miles.map(([t, can, res], k) => `<li class="${res.length ? "" : "soon"}"><a href="milestone.html"><span class="k">${k + 1}</span><b>${esc(t)}</b><p>${esc(can)}</p><span class="r">${res.length ? `자료 ${res.length}개` : "자료 준비 중"}</span></a></li>`).join("")}</ol></div>`;

const home = html("역할별 여정", css, `${header("여정")}<main>
<section class="hero"><div class="wrap"><div><h1>누구나 자기 자리에서<br class="w"> AI/AX를 시작할 수 있게</h1>
<p>개발을 처음 배우는 사람, 회사에서 AX를 맡은 실무자, 팀을 이끄는 사람마다 가는 길이 달라요. 질문 세 개로 어디서 시작하면 좋을지 찾아 드려요.</p>
<div class="facts"><span>${i("lock")}가입 없이 모두 공개</span><span>${i("signpost")}길마다 이정표로 나눠요</span><span>${i("message-square")}현장 의견으로 계속 고쳐요</span></div></div>
<form class="quiz" data-quiz onsubmit="return false"><h2>${i("compass")}어디서 시작할까요?</h2>
${QUIZ.map((q, n) => `<fieldset class="q"><legend>${n + 1}. ${q.q}</legend><div class="opts">${q.a.map(([t, v], k) => `<label><input type="radio" name="q${n}" value="${v}"${k ? "" : " checked"}><span>${t}</span></label>`).join("")}</div></fieldset>`).join("")}
<div class="rec" aria-live="polite"><span class="st">1</span><span><small></small><b></b></span><a href="milestone.html">보러 가기${i("arrow-right")}</a></div>
<p class="note">답은 이 화면에서만 계산하고 어디에도 저장하지 않아요.</p></form></div></section>
<section class="sec"><div class="wrap"><h2>세 가지 길</h2><p class="sub">이정표마다 "이걸 할 수 있게 돼요"를 먼저 적었어요. 아무 이정표나 눌러서 바로 시작해도 돼요.</p>
${JOURNEYS.map(lane).join("")}</div></section>
<section class="sec"><div class="wrap"><h2>어느 길이든 같아요</h2><div class="same">
<div>${i("flag")}<b>할 수 있는 것부터 적어요</b><p>이정표마다 끝나면 무엇을 할 수 있는지 먼저 보여 드려요.</p></div>
<div>${i("list-checks")}<b>과제로 확인해요</b><p>배운 것을 섞어 푸는 연습 과제와 단계별 힌트가 있어요.</p></div>
<div>${i("history")}<b>바뀐 내용을 남겨요</b><p>길과 이정표를 고치면 기록으로 공개해요.</p></div></div>
<ul class="chg">${CHANGES.map(([d, t]) => `<li><time>${d}</time><span>${t}</span></li>`).join("")}</ul></div></section>
</main>${footer}`, kit).replace("</body>", quizJs + "</body>");

const M = MILE, j = M.j, mm = M.m, nm = j.miles[M.n + 1];
const detail = html(`${mm[0]} · 역할별 여정`, css, `${header("여정")}<main style="--c:${j.color}">
<div class="band"><div class="wrap"><a class="back" href="home.html">${i("arrow-left")}${esc(j.who)}의 길</a>
<ol class="trk" aria-label="이정표 위치" style="--n:${j.miles.length}">${j.miles.map((m, k) => `<li class="${k === M.n ? "on" : ""}"><span class="s">${k + 1}</span><span class="l">${esc(m[0])}</span></li>`).join("")}</ol></div></div></div>
<div class="wrap mh"><article><p class="who">${M.n + 1}번째 이정표</p><h1>${esc(mm[0])}</h1><p class="can">이 이정표를 지나면 ${esc(mm[1].replace(/요$/, "요."))}</p>
<section class="blk"><h2>${i("target")}연습 과제</h2><div class="task"><b>${esc(M.task.title)}</b><ol>${M.task.steps.map((s) => `<li><span>${md(s)}</span></li>`).join("")}</ol>
<details><summary>${i("lightbulb")}막히면 힌트 보기</summary><ul>${M.task.hints.map((h) => `<li>${md(h)}</li>`).join("")}</ul></details></div></section>
<section class="blk"><h2>${i("book-open")}배우는 자료</h2><div class="cards">${mm[2].map((c) => `<div class="cd"><img src="../shared/covers/${c.no}.jpg" alt="" loading="lazy"><div><b>${c.no} · ${esc(c.title)}</b><p>${md(c.goal)}</p><nav><a href="${deck(c)}">${i("presentation")}슬라이드</a><a href="${pdf(c)}">${i("download")}PDF</a></nav></div></div>`).join("")}</div></section>
<section class="blk"><h2>${i("circle-check")}스스로 확인해요</h2><ul class="self">${M.check.map((q) => `<li>${i("circle")}<span>${md(q)}</span></li>`).join("")}</ul></section></article>
<aside class="aside"><div class="box"><h3>다음 이정표</h3><a class="nx" href="milestone.html"><span class="s"></span><span><b>${esc(nm[0])}</b><small>${esc(nm[1])}</small></span></a></div>
<div class="box"><h3>다른 길에서 같은 자료를 써요</h3><ul><li>${i("building-2")}AX 실무자 · 데이터 정리하기</li><li>${i("users")}팀 리더 · 같은 자료로 공부하기</li></ul></div>
<div class="box"><h3>이 길이 맞지 않나요?</h3><ul><li>${i("compass")}<a href="home.html">시작점 다시 찾기</a></li><li>${i("message-square")}<a href="#">의견 보내기</a></li></ul></div></aside></div></main>${footer}`, kit);

write("v8", "home.html", home);
write("v8", "milestone.html", detail);
console.log("v8 ok");
