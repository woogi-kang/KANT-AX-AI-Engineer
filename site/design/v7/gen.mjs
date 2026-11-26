// 시안 v7 · 가이드라인 문서. 공공기관 지침서처럼 판과 고친 날을 밝히고, 단계마다 목표, 질문, 체크리스트, 결과물, 함정을 같은 틀로 적어요.
import { i, esc, byNo, write } from "../lib.mjs";
import { PHASES, PHASE, LEVELS, CHANGES, FOOT_NEW, COPY, searchKit, DLG_CSS, items, html, deck, md, VERSION, UPDATED } from "../new/content.mjs";

const css = `:root{--bg:#FFFFFF;--ink:#0B0C0E;--sub:#4D525C;--line:#D5D7DB;--soft:#F3F4F6;--ac:#2459C9;--ac-d:#1A3F91;--bar:#0B0C0E;--bar-ink:#FFFFFF;--warn:#B26A00;--warn-s:#FFF6E6}
[data-theme=dark]{--bg:#111316;--ink:#ECEEF1;--sub:#A7ACB6;--line:#30343B;--soft:#1A1D22;--ac:#86A8F2;--ac-d:#B4C8F7;--bar:#000000;--bar-ink:#ECEEF1;--warn:#E3A64A;--warn-s:#2A2215}
body{background:var(--bg);color:var(--ink);font-size:18px;line-height:1.65}
.wrap{max-width:1080px;margin:0 auto;padding:0 32px}
a.u,.prose a{color:var(--ac);text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px}a.u:hover{text-decoration-thickness:3px;color:var(--ac-d)}
.bar{background:var(--bar);color:var(--bar-ink)}.bar .wrap{display:flex;align-items:center;gap:28px;height:64px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:18px;white-space:nowrap}.brand .i{width:22px;height:22px}
.nav{display:flex;gap:22px;font-size:16px;font-weight:600}.nav a{opacity:.8;padding:20px 0;border-bottom:4px solid transparent}.nav a[aria-current]{opacity:1;border-color:var(--ac)}
.tools{margin-left:auto;display:flex;gap:6px}.tb{height:36px;display:flex;align-items:center;gap:8px;padding:0 10px;border:1px solid rgba(255,255,255,.3);border-radius:4px;background:none;color:inherit;cursor:pointer;font-size:15px}
.tb kbd{font-size:12px;opacity:.7}[data-theme=light] .tb .moon-i,[data-theme=dark] .tb .sun-i{display:none}
.ver{border-bottom:1px solid var(--line);font-size:15px;color:var(--sub)}.ver .wrap{display:flex;gap:10px 18px;align-items:center;padding-top:10px;padding-bottom:10px;flex-wrap:wrap}
.chip{display:inline-block;font-size:13px;font-weight:800;letter-spacing:.02em;background:var(--ink);color:var(--bg);padding:2px 8px}
.top{padding:56px 0 40px}.top h1{font-size:48px;line-height:1.2;letter-spacing:-.025em;max-width:800px}
.lead{font-size:22px;line-height:1.55;color:var(--sub);margin-top:18px;max-width:760px}
.doors{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:40px}
.door{display:block;border-top:6px solid var(--ink);padding:20px 0 0}.door small{font-size:15px;color:var(--sub);font-weight:600}
.door h2{font-size:26px;letter-spacing:-.015em;margin:4px 0 8px;color:var(--ac);text-decoration:underline;text-underline-offset:4px;text-decoration-thickness:2px}.door p{color:var(--sub)}
.door:hover h2{text-decoration-thickness:4px}
.sec{padding:48px 0;border-top:1px solid var(--line)}.sec h2{font-size:32px;letter-spacing:-.02em}.sec>.wrap>p{color:var(--sub);margin-top:8px;max-width:720px}
.steps{list-style:none;margin:28px 0 0;padding:0;max-width:820px;position:relative}
.steps li{position:relative;padding:0 0 28px 64px}.steps li::before{content:"";position:absolute;left:19px;top:40px;bottom:0;width:2px;background:var(--line)}.steps li:last-child::before{display:none}
.num{position:absolute;left:0;top:0;width:40px;height:40px;border-radius:50%;border:2px solid var(--ink);background:var(--bg);display:grid;place-items:center;font-weight:800;font-size:17px}
.steps h3{font-size:22px;line-height:40px}.steps h3 a{color:var(--ac);text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px}.steps p{color:var(--sub)}
.steps .tags{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}.steps .tags span{font-size:14px;border:1px solid var(--line);padding:1px 8px;color:var(--sub)}
.lvl{width:100%;border-collapse:collapse;margin-top:24px;max-width:820px}.lvl th,.lvl td{text-align:left;padding:14px 16px 14px 0;border-bottom:1px solid var(--line);vertical-align:top}.lvl th{width:120px;font-size:17px}
.princ{display:grid;grid-template-columns:repeat(2,1fr);gap:28px 40px;margin-top:28px;max-width:900px}.princ b{display:block;font-size:19px}.princ p{color:var(--sub);margin-top:4px}
.howto{display:grid;grid-template-columns:1.2fr 1fr;gap:48px;align-items:start}
.log{list-style:none;padding:0;margin:20px 0 0}.log li{display:flex;gap:18px;padding:12px 0;border-bottom:1px solid var(--line);font-size:17px}.log time{font-size:15px;color:var(--sub);width:100px;flex:none;padding-top:1px}
.inset{border-left:8px solid var(--line);padding:6px 0 6px 20px;margin-top:20px;color:var(--ink)}
.btn{display:inline-flex;align-items:center;gap:8px;background:var(--ac);color:#fff;font-weight:700;padding:10px 18px;border-radius:4px;box-shadow:0 3px 0 var(--ac-d);margin-top:20px}
.ft{background:var(--soft);border-top:4px solid var(--ac);padding:32px 0 44px;font-size:15px;color:var(--sub)}.ft .wrap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
/* 단계 문서 */
.crumb{font-size:15px;padding:18px 0 0;display:flex;gap:8px;flex-wrap:wrap;align-items:center}.crumb .i{width:14px;height:14px;color:var(--sub)}
.doc{display:grid;grid-template-columns:280px minmax(0,1fr);gap:56px;padding:28px 0 72px}
.snav{position:sticky;top:20px;align-self:start;font-size:16px}.doc .snav h2{font-size:15px;color:var(--sub);font-weight:600;margin:0 0 12px;letter-spacing:0}
.snav ol{list-style:none;padding:0;margin:0}.snav>ol>li{position:relative;padding:0 0 16px 40px}.snav>ol>li::before{content:"";position:absolute;left:13px;top:28px;bottom:0;width:2px;background:var(--line)}.snav>ol>li:last-child::before{display:none}
.snav .n{position:absolute;left:0;top:0;width:28px;height:28px;border-radius:50%;border:2px solid var(--ink);display:grid;place-items:center;font-size:14px;font-weight:800;background:var(--bg)}
.snav a{color:var(--ac);text-decoration:underline;text-underline-offset:3px;line-height:28px}.snav li.on>a{color:var(--ink);font-weight:800;text-decoration:none}.snav li.on .n{background:var(--ink);color:var(--bg)}
.snav ul{list-style:none;padding:6px 0 0;margin:0;border-left:3px solid var(--ink);padding-left:12px}.snav ul a{display:block;line-height:1.4;padding:4px 0;font-size:15px}
.kick{font-size:20px;color:var(--sub);font-weight:600}.doc h1{font-size:44px;letter-spacing:-.025em;line-height:1.2;margin-top:4px}
.doc h2{font-size:28px;letter-spacing:-.015em;margin:48px 0 14px;scroll-margin-top:20px}
.qs{margin:0;padding-left:24px}.qs li{padding:4px 0}
.cl{list-style:none;padding:0;margin:0}.cl li{display:flex;gap:14px;align-items:flex-start;padding:10px 0}
.cl input{appearance:none;width:28px;height:28px;flex:none;border:2px solid var(--ink);margin:0;display:grid;place-items:center;cursor:pointer;background:var(--bg)}.cl input:checked::after{content:"";width:14px;height:8px;border-left:3px solid var(--ink);border-bottom:3px solid var(--ink);transform:rotate(-45deg) translate(1px,-2px)}
.cl label{cursor:pointer;padding-top:1px}.small{font-size:15px;color:var(--sub);margin-top:6px}
.tbl{width:100%;border-collapse:collapse}.tbl th,.tbl td{text-align:left;padding:12px 16px 12px 0;border-bottom:1px solid var(--line);vertical-align:top}.tbl th{font-size:16px;border-bottom:2px solid var(--ink)}
.warn{border-left:8px solid var(--warn);background:var(--warn-s);padding:18px 22px}.warn h3{display:flex;gap:10px;align-items:center;font-size:19px;margin:16px 0 4px}.warn h3:first-child{margin-top:0}.warn .i{color:var(--warn);width:22px;height:22px}.warn p{color:var(--ink)}
.roles{display:grid;grid-template-columns:1fr 1fr;gap:0 32px}.roles div{padding:12px 0;border-bottom:1px solid var(--line)}.roles b{display:block}.roles p{color:var(--sub);font-size:17px}
.rel{list-style:none;padding:0;margin:0}.rel li{padding:8px 0;display:flex;gap:10px;align-items:baseline}.rel small{color:var(--sub);font-size:15px}
.pn{display:flex;justify-content:space-between;gap:24px;margin-top:56px;padding-top:24px;border-top:1px solid var(--line)}.pn a{display:flex;flex-direction:column;gap:2px;max-width:50%}.pn small{font-size:15px;color:var(--sub);display:flex;gap:6px;align-items:center}.pn small .i{width:15px;height:15px}.pn b{color:var(--ac);text-decoration:underline;text-underline-offset:3px;font-size:19px}
.pn a:last-child{text-align:right;align-items:flex-end}
.meta{margin-top:40px;background:var(--soft);padding:18px 22px;font-size:16px;display:flex;flex-wrap:wrap;gap:8px 24px;align-items:center}.meta a{display:inline-flex;gap:6px;align-items:center}
${DLG_CSS({ scrim: "rgba(0,0,0,.45)", bg: "var(--bg)", ink: "var(--ink)", line: "var(--line)", r: "4px", sub: "var(--sub)", hover: "var(--soft)" })}
@media (max-width:900px){.snav ul{display:none}.doc{grid-template-columns:1fr;gap:28px}.snav{position:static;border:1px solid var(--line);padding:16px}.howto{grid-template-columns:1fr}}
@media (max-width:760px){body{font-size:17px}.wrap{padding:0 16px}.nav{display:none}.tb span,.tb kbd{display:none}.top{padding:36px 0 28px}.top h1,.doc h1{font-size:32px}.lead{font-size:19px}
.doors,.princ,.roles{grid-template-columns:1fr}.sec h2{font-size:26px}.doc h2{font-size:24px}.lvl th{width:76px}.steps li{padding-left:56px}.pn{flex-direction:column}.pn a{max-width:none}.pn a:last-child{text-align:left;align-items:flex-start}}`;

const header = (cur) => `<header class="bar"><div class="wrap"><a class="brand" href="home.html">${i("book-open")}풀스택 AI/AX 가이드라인</a>
<nav class="nav" aria-label="메뉴">${[["가이드라인", "home.html"], ["역량 기준", "#levels"], ["꿀팁", "#"], ["소식", "#"]].map(([t, h]) => `<a href="${h}"${t === cur ? ' aria-current="page"' : ""}>${t}</a>`).join("")}</nav>
<div class="tools"><button class="tb" data-search>${i("search")}<span>찾기</span><kbd>/</kbd></button><button class="tb" data-theme-toggle aria-label="화면 밝기 바꾸기">${i("moon", "i moon-i")}${i("sun", "i sun-i")}</button></div></div></header>
<div class="ver"><div class="wrap"><span class="chip">${VERSION}</span><span>마지막 고침 ${UPDATED}</span><span>누구나 고치자고 제안할 수 있어요 · <a class="u" href="#">고치기 제안</a></span></div></div>`;
const footer = `<footer class="ft"><div class="wrap"><span>${FOOT_NEW} 회사 안에서 자유롭게 읽고 함께 봐도 돼요.</span><span>${COPY}</span></div></footer>`;
const kit = searchKit(items, "phase.html");
const ROLE_TAG = ["경영진", "현업 담당", "현업 담당 · 데이터 담당", "경영진 · 현업 담당", "현업 담당 · 교육 담당", "IT · 보안 · 법무"];

const home = html("AX 도입 가이드라인", css, `${header("가이드라인")}<main>
<section class="top"><div class="wrap"><h1>모든 회사의 AX 도입을 위한 공개 가이드라인</h1>
<p class="lead">IT 회사가 아니어도 AI를 업무에 들여올 수 있게, 무엇을 어떤 순서로 정하고 확인하면 되는지 단계별로 적었어요. 함께 일할 엔지니어가 갖출 역량도 같이 정리해요.</p>
<div class="doors"><a class="door" href="#phases"><small>실무자와 경영진을 위한 문서</small><h2>기업 AX 도입 가이드라인</h2><p>방향을 정하는 데서 운영까지 여섯 단계로 나눠, 단계마다 물어볼 것과 남길 결과물을 적었어요.</p></a>
<a class="door" href="#levels"><small>엔지니어를 준비하는 사람을 위한 문서</small><h2>AI/AX 엔지니어 역량 기준</h2><p>도구, 코드, 데이터, 환경, AI 다섯 영역에서 무엇을 할 수 있으면 되는지와 배울 자료를 이어 뒀어요.</p></a></div></div></section>
<section class="sec" id="phases"><div class="wrap"><h2>도입 여섯 단계</h2><p>단계는 순서대로 읽는 것을 권해요. 이미 지난 단계가 있으면 체크리스트로 빠진 것만 확인해도 돼요.</p>
<ol class="steps">${PHASES.map((p, k) => `<li><span class="num">${p.no}</span><h3><a href="phase.html">${esc(p.title)}</a></h3><p>${esc(p.sum)}</p><div class="tags"><span>${ROLE_TAG[k]}</span></div></li>`).join("")}</ol></div></section>
<section class="sec" id="levels"><div class="wrap"><h2>AI/AX 엔지니어 역량 기준</h2><p>영역마다 "할 수 있어요"로 적었어요. 각 줄을 누르면 그 역량을 기르는 자료로 이어져요.</p>
<table class="lvl"><tbody>${LEVELS.map(([a, b]) => `<tr><th>${a}</th><td><a class="u" href="#">${b}</a></td></tr>`).join("")}</tbody></table></div></section>
<section class="sec"><div class="wrap"><h2>이 가이드라인을 만드는 원칙</h2><div class="princ">
<div><b>누구나 무료로 봐요</b><p>가입이나 결제 없이 모든 문서와 자료를 공개해요.</p></div>
<div><b>실제로 해 본 것만 적어요</b><p>예시 화면과 출력은 직접 실행한 결과예요. 지어낸 숫자는 넣지 않아요.</p></div>
<div><b>어느 업종이든 쓸 수 있게</b><p>특정 회사나 도구에 묶이지 않는 말로 적어요.</p></div>
<div><b>고친 기록을 남겨요</b><p>판마다 무엇이 바뀌었는지 모두 공개해요.</p></div></div></div></section>
<section class="sec"><div class="wrap howto"><div><h2>고친 기록</h2><ul class="log">${CHANGES.map(([d, t]) => `<li><time>${d}</time><span>${t}</span></li>`).join("")}</ul><p class="small" style="margin-top:14px"><a class="u" href="#">고친 기록 전체 보기</a></p></div>
<div><h2>함께 고쳐요</h2><p class="inset">현장에서 써 보고 맞지 않는 곳이 있으면 알려 주세요. 다음 판에 반영하고 기록에 남겨요.</p><a class="btn" href="#">${i("pencil")}고치기 제안하기</a></div></div></section>
</main>${footer}`, kit);

const P = PHASE, prevP = PHASES[1], nextP = PHASES[3];
const ids = ["goal", "ask", "check", "out", "trap", "who", "rel"];
const detail = html(`${P.no}단계 ${P.title} · AX 도입 가이드라인`, css, `${header("가이드라인")}<main class="wrap">
<nav class="crumb" aria-label="현재 위치"><a class="u" href="home.html">가이드라인</a>${i("chevron-right")}<a class="u" href="home.html#phases">기업 AX 도입 가이드라인</a>${i("chevron-right")}<span>${P.no}단계</span></nav>
<div class="doc"><nav class="snav" aria-label="단계"><h2>기업 AX 도입 여섯 단계</h2><ol>${PHASES.map((p) => `<li class="${p.no === P.no ? "on" : ""}"><span class="n">${p.no}</span><a href="phase.html">${esc(p.title)}</a>${p.no === P.no ? `<ul>${P.sections.map((s, k) => `<li><a href="#${ids[k]}">${s}</a></li>`).join("")}</ul>` : ""}</li>`).join("")}</ol></nav>
<article><p class="kick">${P.no}단계</p><h1>${esc(P.title)}</h1>
<h2 id="goal">목표</h2><p>${esc(P.goal)}</p>
<h2 id="ask">먼저 물어볼 것</h2><ul class="qs">${P.questions.map((q) => `<li>${esc(q)}</li>`).join("")}</ul>
<h2 id="check">체크리스트</h2><ul class="cl">${P.checklist.map((c, k) => `<li><input type="checkbox" id="c${k}"><label for="c${k}">${esc(c)}</label></li>`).join("")}</ul><p class="small">표시는 이 화면에서만 보이고 저장하지 않아요. 회의 때 화면에 띄워 같이 확인해 보세요.</p>
<h2 id="out">결과물</h2><table class="tbl"><thead><tr><th>결과물</th><th>누가</th><th>모양</th></tr></thead><tbody>${P.outputs.map((r) => `<tr>${r.map((x, k) => `<td>${k ? esc(x) : `<a class="u" href="#">${esc(x)}</a>`}</td>`).join("")}</tr>`).join("")}</tbody></table>
<h2 id="trap">흔한 함정</h2><div class="warn">${P.pitfalls.map(([t, d]) => `<h3>${i("triangle-alert")}${esc(t)}</h3><p>${esc(d)}</p>`).join("")}</div>
<h2 id="who">누가 하나요</h2><div class="roles">${P.roles.map(([a, b]) => `<div><b>${a}</b><p>${b}</p></div>`).join("")}</div>
<h2 id="rel">관련 자료</h2><ul class="rel">${P.res.map((n) => byNo[n]).map((c) => `<li>${i("presentation")}<span><a class="u" href="${deck(c)}">${c.no} ${esc(c.title)}</a><br><small>${md(c.goal)}</small></span></li>`).join("")}</ul>
<div class="pn"><a href="phase.html"><small>${i("arrow-left")}이전 단계</small><b>${prevP.no}. ${esc(prevP.title)}</b></a><a href="phase.html"><small>다음 단계${i("arrow-right")}</small><b>${nextP.no}. ${esc(nextP.title)}</b></a></div>
<div class="meta"><span>${VERSION} · 마지막 고침 ${UPDATED}</span><a class="u" href="#">${i("pencil")}이 쪽 고치기 제안</a><a class="u" href="#">${i("history")}이 쪽 고친 기록</a></div>
</article></div></main>${footer}`, kit);

write("v7", "home.html", home);
write("v7", "phase.html", detail);
console.log("v7 ok");
