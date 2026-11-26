// 시안 v6 · 로드맵 지도. 역할을 고르면 단계와 주제가 한 장의 지도로 나와요. 주제를 누르면 그 주제의 자료가 모여 있어요.
import { i, esc, write } from "../lib.mjs";
import { ROLES, ROADMAP, TOPIC, topicById, CHANGES, FOOT_NEW, COPY, searchKit, DLG_CSS, items, html, deck, pdf, md, VERSION, UPDATED } from "../new/content.mjs";

const css = `:root{--bg:#FFFFFF;--paper:#F5F4EF;--ink:#16181D;--sub:#5B6070;--mute:#8A8F9C;--line:#DCDAD2;--line2:#C9C6BC;--ac:#2459C9;--ac-s:#E9EFFC;--node:#16181D;--node-ink:#FFFFFF;--ok:#1F8A4C}
[data-theme=dark]{--bg:#121418;--paper:#181B21;--ink:#ECEDEF;--sub:#A3A8B3;--mute:#7C818D;--line:#2B2F38;--line2:#3A3F4A;--ac:#7FA2F0;--ac-s:#1D2740;--node:#ECEDEF;--node-ink:#121418;--ok:#5CC08A}
body{background:var(--bg);color:var(--ink);font-size:16px;line-height:1.6}
.wrap{max-width:1200px;margin:0 auto;padding:0 24px}
.hd{border-bottom:1px solid var(--line);background:var(--bg);position:sticky;top:0;z-index:10}
.hd .wrap{display:flex;align-items:center;gap:24px;height:60px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;letter-spacing:-.01em;white-space:nowrap}
.brand-m{width:28px;height:28px;border-radius:7px;background:var(--node);color:var(--node-ink);display:grid;place-items:center}.brand-m .i{width:16px;height:16px}
.nav{display:flex;gap:4px}.nav a{padding:6px 10px;border-radius:6px;color:var(--sub);font-weight:600;font-size:15px}.nav a[aria-current]{color:var(--ink);background:var(--paper)}
.tools{margin-left:auto;display:flex;gap:8px;align-items:center}
.sbtn{display:flex;align-items:center;gap:8px;height:36px;padding:0 10px 0 12px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--sub);cursor:pointer;font-size:14px;min-width:200px}.sbtn kbd{margin-left:auto;font-size:12px;border:1px solid var(--line);border-radius:5px;padding:0 6px}
.ibtn{width:36px;height:36px;display:grid;place-items:center;border:1px solid var(--line);border-radius:8px;background:var(--bg);cursor:pointer}
[data-theme=light] .ibtn .moon-i,[data-theme=dark] .ibtn .sun-i{display:none}
.hero{padding:56px 0 28px}
.hero h1{font-size:44px;line-height:1.25;letter-spacing:-.025em;font-weight:800;max-width:780px}
.hero p{margin-top:14px;color:var(--sub);font-size:18px;max-width:680px}
.roles{display:flex;gap:12px;margin-top:28px;flex-wrap:wrap}
.role{display:flex;gap:12px;align-items:flex-start;text-align:left;padding:14px 18px 14px 14px;border:1.5px solid var(--line);border-radius:12px;background:var(--bg);cursor:pointer;min-width:280px}
.role .i{width:22px;height:22px;margin-top:2px;color:var(--sub)}.role b{display:block;font-size:16px}.role small{color:var(--sub);font-size:14px}
.role[aria-selected=true]{border-color:var(--ink);box-shadow:inset 0 0 0 1px var(--ink)}.role[aria-selected=true] .i{color:var(--ac)}
.legend{display:flex;gap:20px;flex-wrap:wrap;align-items:center;padding:14px 0;margin-top:8px;color:var(--sub);font-size:14px}
.lg{display:flex;align-items:center;gap:8px}.lg i{display:block;width:22px;height:14px;border-radius:4px;border:2px solid var(--ink)}.lg i.dash{border-style:dashed;border-color:var(--mute)}
.dot{width:8px;height:8px;border-radius:50%;background:var(--ac);flex:none}.dot.off{background:none;border:1.5px solid var(--mute)}
.mapbox{background:var(--paper);background-image:radial-gradient(var(--line) 1px,transparent 1px);background-size:22px 22px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:48px 0 56px}
.map{position:relative;max-width:1040px;margin:0 auto}
.map::before{content:"";position:absolute;left:50%;top:0;bottom:0;width:3px;margin-left:-1.5px;background:var(--ink);border-radius:2px}
.st{position:relative;display:grid;grid-template-columns:1fr 280px 1fr;gap:0 40px;align-items:center;padding:20px 0}
.st-node{grid-column:2;grid-row:1/span 9;align-self:center;position:relative;z-index:1;background:var(--node);color:var(--node-ink);border-radius:12px;padding:14px 16px}
.st-node small{font-size:13px;opacity:.7;font-weight:600}.st-node h3{font-size:18px;line-height:1.35;margin-top:2px}.st-node p{font-size:14px;opacity:.78;margin-top:4px;line-height:1.5}
.tp{position:relative;display:block;background:var(--bg);border:2px solid var(--ink);border-radius:10px;padding:10px 14px;margin:6px 0}
.tp.opt{border-style:dashed;border-color:var(--mute)}
.tp::after{content:"";position:absolute;top:50%;width:40px;height:2px;background:var(--line2)}
.tp.l{grid-column:1}.tp.l::after{right:-42px}.tp.r{grid-column:3}.tp.r::after{left:-42px}
.tp b{display:flex;align-items:center;gap:8px;font-size:16px;line-height:1.4}.tp p{color:var(--sub);font-size:14px;line-height:1.5;margin-top:2px}
.tp .meta{display:flex;align-items:center;gap:6px;margin-top:6px;font-size:13px;color:var(--ac);font-weight:600}.tp.soon .meta{color:var(--mute);font-weight:500}
.tp:hover{box-shadow:0 0 0 3px var(--ac-s);border-color:var(--ac)}
.tp.here{background:var(--ac-s);border-color:var(--ac)}
.grow{padding:56px 0}.grow .wrap{display:grid;grid-template-columns:1fr 1fr;gap:48px}
.grow h2{font-size:24px;letter-spacing:-.015em}.grow p{color:var(--sub);margin-top:8px}
.chg{list-style:none;padding:0;margin:14px 0 0;border-top:1px solid var(--line)}.chg li{display:flex;gap:16px;padding:12px 0;border-bottom:1px solid var(--line)}.chg time{color:var(--mute);font-size:14px;flex:none;width:96px}
.btn{display:inline-flex;align-items:center;gap:8px;height:42px;padding:0 16px;border-radius:9px;font-weight:700;border:1.5px solid var(--ink)}.btn.pri{background:var(--ink);color:var(--bg)}
.btns{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
.ft{border-top:1px solid var(--line);padding:28px 0 40px;color:var(--sub);font-size:14px}.ft .wrap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
/* 주제 화면 */
.crumb{display:flex;gap:6px;align-items:center;flex-wrap:wrap;color:var(--sub);font-size:14px;padding:20px 0 0}.crumb .i{width:14px;height:14px}.crumb a:hover{color:var(--ink)}
.tpage{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:56px;padding:24px 0 64px}
.kick{color:var(--sub);font-size:15px;font-weight:600}
.tpage h1{font-size:38px;letter-spacing:-.025em;line-height:1.25;margin-top:6px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.tag{font-size:13px;font-weight:700;border:1.5px solid var(--ink);border-radius:6px;padding:1px 8px;letter-spacing:0}
.lede{font-size:18px;color:var(--sub);margin-top:14px;max-width:680px}
.blk{margin-top:40px}.blk h2{font-size:20px;letter-spacing:-.01em;margin-bottom:12px}
.can{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:1fr 1fr;gap:10px}
.can li{display:flex;gap:10px;align-items:flex-start;padding:12px 14px;border:1px solid var(--line);border-radius:10px}.can .i{color:var(--ok);margin-top:3px}
.pre{display:inline-flex;align-items:center;gap:10px;padding:10px 14px;border:2px solid var(--ink);border-radius:10px}.pre small{color:var(--sub)}
.res{list-style:none;padding:0;margin:0;border-top:1px solid var(--line)}
.res li{display:grid;grid-template-columns:128px minmax(0,1fr) auto;gap:18px;align-items:center;padding:14px 0;border-bottom:1px solid var(--line)}
.res img{width:128px;aspect-ratio:16/9;object-fit:cover;border-radius:6px;border:1px solid var(--line)}
.res b{display:block;line-height:1.4}.res .no{color:var(--mute);font-weight:600;margin-right:6px}.res p{color:var(--sub);font-size:14px;margin-top:2px}
.res .acts{display:flex;gap:6px}.res .acts a{display:inline-flex;align-items:center;gap:6px;height:34px;padding:0 12px;border:1px solid var(--line);border-radius:8px;font-size:14px;font-weight:600;white-space:nowrap}.res .acts a:first-child{border-color:var(--ink)}
.res .acts .i{width:15px;height:15px}
.nextc{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:18px 20px;border:2px solid var(--ink);border-radius:12px}.nextc small{color:var(--sub)}.nextc b{font-size:18px;display:block}
.side{position:sticky;top:84px;align-self:start}
.mini{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:18px}
.mini h3{font-size:14px;color:var(--sub);font-weight:600}.mini .sn{font-size:17px;font-weight:800;margin:2px 0 12px}
.mini ol{list-style:none;padding:0 0 0 18px;margin:0;position:relative}.mini ol::before{content:"";position:absolute;left:5px;top:8px;bottom:8px;width:2px;background:var(--ink)}
.mini li{position:relative;padding:6px 0;font-size:15px}.mini li::before{content:"";position:absolute;left:-18px;top:13px;width:12px;height:12px;border-radius:50%;background:var(--bg);border:2px solid var(--ink)}
.mini li.opt::before{border-style:dashed;border-color:var(--mute)}.mini li.here{font-weight:800;color:var(--ac)}.mini li.here::before{background:var(--ac);border-color:var(--ac)}
.mini .stg{display:flex;justify-content:space-between;gap:8px;margin-top:14px;padding-top:12px;border-top:1px solid var(--line);font-size:14px;color:var(--sub)}
.note{margin-top:14px;font-size:13px;color:var(--mute);line-height:1.5}
${DLG_CSS({ scrim: "rgba(10,12,16,.35)", bg: "var(--bg)", ink: "var(--ink)", line: "var(--line)", r: "12px", sub: "var(--sub)", hover: "var(--paper)" })}
@media (max-width:1100px){.sbtn{min-width:0}.sbtn span,.sbtn kbd{display:none}}
@media (max-width:960px){.st{grid-template-columns:1fr 240px 1fr;gap:0 28px}.tp.l::after{right:-30px;width:28px}.tp.r::after{left:-30px;width:28px}.tpage{grid-template-columns:1fr}.side{position:static}}
@media (max-width:760px){.wrap{padding:0 16px}.nav{display:none}.hero{padding:36px 0 20px}.hero h1{font-size:30px}.hero p{font-size:16px}.role{min-width:0;flex:1 1 100%}
.mapbox{padding:28px 16px 36px}.map::before{left:9px}.st{display:block;padding:10px 0 10px 32px}.st-node{margin-bottom:8px}.st-node::before{content:"";position:absolute;left:-29px;top:20px;width:14px;height:14px;border-radius:50%;background:var(--node);box-shadow:0 0 0 4px var(--paper)}
.tp::after{display:none}.grow .wrap{grid-template-columns:1fr;gap:36px}.tpage h1{font-size:28px}.can{grid-template-columns:1fr}
.res li{grid-template-columns:88px minmax(0,1fr)}.res img{width:88px}.res .acts{grid-column:1/-1}}`;

const header = (cur) => `<header class="hd"><div class="wrap"><a class="brand" href="home.html"><span class="brand-m">${i("route")}</span>풀스택 AI/AX 로드맵</a>
<nav class="nav" aria-label="메뉴">${[["로드맵", "home.html"], ["가이드라인", "#"], ["꿀팁", "#"], ["소식", "#"]].map(([t, h]) => `<a href="${h}"${t === cur ? ' aria-current="page"' : ""}>${t}</a>`).join("")}</nav>
<div class="tools"><button class="sbtn" data-search aria-label="찾기">${i("search")}<span>주제 찾기</span><kbd>/</kbd></button><button class="ibtn" data-theme-toggle aria-label="화면 밝기 바꾸기">${i("moon", "i moon-i")}${i("sun", "i sun-i")}</button></div></div></header>`;
const footer = `<footer class="ft"><div class="wrap"><span>${FOOT_NEW}</span><span>${COPY}</span></div></footer>`;
const kit = searchKit(items, "topic.html");

const topicCard = (t, side) => `<a class="tp ${side}${t.need ? "" : " opt"}${t.ready ? "" : " soon"}${t.id === "sql" ? " here" : ""}" href="topic.html" data-t>
<b>${esc(t.title)}</b><p>${esc(t.sum)}</p><span class="meta">${t.ready ? `<span class="dot"></span>자료 ${t.res.length}개` : `<span class="dot off"></span>준비 중`}</span></a>`;
const mapOf = (r) => `<div class="map" data-panel="${r}"${r === "eng" ? "" : " hidden"}>${ROADMAP[r].map((s) => `<section class="st" aria-label="${s.no}단계">
<div class="st-node"><small>${s.no}단계</small><h3>${esc(s.title)}</h3><p>${esc(s.sum)}</p></div>
${s.topics.map((t, k) => topicCard(t, k % 2 ? "r" : "l")).join("")}</section>`).join("")}</div>`;

const home = html("로드맵 지도", css, `${header("로드맵")}<main>
<section class="hero"><div class="wrap"><h1>AI/AX를 준비하는 사람을 위한<br class="w"> 한 장짜리 공개 로드맵</h1>
<p>어디서 시작해서 무엇을 어떤 순서로 배우면 되는지 지도로 보여 드려요. 주제를 누르면 그 주제를 배우는 자료가 모여 있어요.</p>
<div class="roles" data-tabs role="tablist" aria-label="역할 고르기">${ROLES.map((r, k) => `<button class="role" role="tab" data-tab="${r.id}" aria-selected="${!k}">${i(r.icon)}<span><b>${r.name}</b><small>${r.goal}</small></span></button>`).join("")}</div>
<div class="legend"><span class="lg"><i></i>꼭 거쳐 가요</span><span class="lg"><i class="dash"></i>필요하면 봐요</span><span class="lg"><span class="dot"></span>자료 있음</span><span class="lg"><span class="dot off"></span>준비 중</span></div></div></section>
<div class="mapbox">${mapOf("eng")}${mapOf("ax")}</div>
<section class="grow"><div class="wrap"><div><h2>지도는 계속 자라요</h2><p>현장에서 받은 질문과 의견으로 주제를 더하고 고쳐요. 바뀐 내용은 모두 기록으로 남겨요.</p>
<ul class="chg">${CHANGES.map(([d, t]) => `<li><time>${d}</time><span>${t}</span></li>`).join("")}</ul></div>
<div><h2>함께 만들어요</h2><p>빠진 주제나 틀린 곳이 보이면 알려 주세요. 회사에서 AX를 준비하며 겪은 일도 다음 사람에게 큰 도움이 돼요.</p>
<div class="btns"><a class="btn pri" href="#">${i("message-square")}의견 보내기</a><a class="btn" href="#">${i("history")}바뀐 내용 전체 보기</a></div>
<p class="note">${VERSION} · 마지막 고침 ${UPDATED}</p></div></div></section></main>${footer}`, kit);

const T = TOPIC, S = T.stage, nxt = topicById[T.after], pre = topicById[T.before[0]];
const detail = html("SQL로 골라 보고 고치기 · 로드맵", css, `${header("로드맵")}<main class="wrap">
<nav class="crumb" aria-label="현재 위치"><a href="home.html">로드맵</a>${i("chevron-right")}<span>엔지니어 준비</span>${i("chevron-right")}<span>${S.no}단계 ${esc(S.title)}</span></nav>
<div class="tpage"><article>
<p class="kick">${S.no}단계 · ${esc(S.title)}</p><h1>${esc(T.title)}<span class="tag">꼭 거쳐 가요</span></h1>
<p class="lede">${esc(T.why)}</p>
<section class="blk"><h2>이 주제를 마치면</h2><ul class="can">${T.can.map((x) => `<li>${i("check")}<span>${x}</span></li>`).join("")}</ul></section>
<section class="blk"><h2>먼저 보면 좋아요</h2><a class="pre" href="topic.html">${i("arrow-left")}<span><b>${esc(pre.title)}</b> <small>${esc(pre.sum)}</small></span></a></section>
<section class="blk"><h2>배우는 자료 ${T.res.length}개</h2><ul class="res">${T.res.map((c) => `<li><img src="../shared/covers/${c.no}.jpg" alt="" loading="lazy">
<div><b><span class="no">${c.no}</span>${esc(c.title)}</b><p>${md(c.goal)}</p></div><div class="acts"><a href="${deck(c)}">${i("presentation")}슬라이드</a><a href="${pdf(c)}">${i("download")}PDF</a></div></li>`).join("")}</ul></section>
<section class="blk"><h2>다음 주제</h2><a class="nextc" href="topic.html"><span><small>${S.no}단계 · 이어서</small><b>${esc(nxt.title)}</b></span>${i("arrow-right")}</a></section>
</article>
<aside class="side"><div class="mini"><h3>지금 보는 단계</h3><p class="sn">${S.no}. ${esc(S.title)}</p>
<ol>${S.topics.map((t) => `<li class="${t.need ? "" : "opt "}${t.id === T.id ? "here" : ""}">${esc(t.title)}</li>`).join("")}</ol>
<div class="stg"><a href="topic.html">${i("chevron-left", "i")}</a><a href="home.html">지도에서 보기</a><a href="topic.html">${i("chevron-right", "i")}</a></div></div>
<p class="note">진도는 저장하지 않아요. 가입 없이 언제든 처음부터 다시 볼 수 있어요.</p></aside></div></main>${footer}`, kit);

write("v6", "home.html", home);
write("v6", "topic.html", detail);
console.log("v6 ok");
