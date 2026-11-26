// 시안 v16 · 핸드북, 그림은 크게 글은 적게. v15 틀(왼쪽 목차, 찾기)은 두고 첫 화면에서 읽을 글을 줄였어요.
// 로고는 devicon(MIT)의 공식 컬러 로고, uv만 Simple Icons(CC0). 긴 설명과 로드맵 본문은 펼쳐 보기 안에 둬요.
import * as D from "../plan/data.mjs";
const { i, esc, S, byNo, short, stageShort, TOPIC, CH, LIB, NEWS, MENU, FOOT, LIC, html, DLG_CSS, kitFor, AREAS, stageTopics, stageCount, STAGE_LINKS, AREA_LINKS, lecStages } = D;
import { write } from "../lib.mjs";

const STAGE_IC = { 1: "compass", 2: "layers", 3: "workflow", 4: "flag", 5: "building-2" };
const AREA_IC = { "software-and-api": "plug", "llm-foundations": "brain", "agent-systems": "bot", "tools-and-mcp": "wrench", "evaluation-and-testing": "gauge", "production-operations": "activity", "security-and-privacy": "shield-check" };
const LIB_IC = { cases: "briefcase", public: "file-check-2", failures: "triangle-alert", templates: "clipboard-check", jobs: "chart-column" };
const CASE_IC = { "고객·매출": "messages-square", "사람·협업": "users", "재무·구매": "receipt", "데이터·운영": "database", "공통 기능·운영": "layers" };
const START = [["square-terminal", "개발이 처음이에요", "roadmap.html"], ["code-xml", "개발 경험이 있어요", "roadmap.html"], ["briefcase", "업무는 잘 알아요", "roadmap.html"], ["book-a", "용어부터 낯설어요", "#"], ["play", "코드부터 돌려 볼래요", "cases.html"], ["presentation", "수업을 듣고 있어요", "chapter.html"]];
const LOGO_FILE = { terminal: "bash" };
const lg = (k, sz = 28) => `<img class="lg" src="../shared/logos/${LOGO_FILE[k] || k}.svg" alt="" width="${sz}" height="${sz}" style="--s:${sz}px">`;
const lgs = (ks, sz) => `<span class="lgs">${ks.map((k) => lg(k, sz)).join("")}</span>`;
const cover = (n) => `../shared/covers/${n}.jpg`;
const ict = (n, cls = "") => `<span class="ict ${cls}">${i(n)}</span>`;

const css = `:root{--bg:#fff;--side:#FAFAF9;--ink:#1D2330;--sub:#5F6675;--mute:#9298A4;--line:#EAE9E6;--line2:#D9D7D2;--ac:#2459C9;--ac-s:#EEF3FD;--code:#F4F3F0}
body{background:var(--bg);color:var(--ink);font-size:16px;line-height:1.6}
.lg{width:var(--s);height:var(--s);object-fit:contain;flex:none}.lgs{display:inline-flex;gap:8px;align-items:center;flex-wrap:wrap}
.ict{width:40px;height:40px;border-radius:11px;background:var(--ac-s);color:var(--ac);display:grid;place-items:center;flex:none}.ict svg{width:22px;height:22px}
.ict.sm{width:28px;height:28px;border-radius:8px}.ict.sm svg{width:16px;height:16px}.ict.lg2{width:56px;height:56px;border-radius:15px}.ict.lg2 svg{width:30px;height:30px;stroke-width:1.6}.ict.n{background:var(--code);color:var(--ink)}
.top{height:60px;border-bottom:1px solid var(--line);display:grid;grid-template-columns:260px minmax(0,1fr) auto;align-items:center;position:sticky;top:0;background:#fff;z-index:5}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;padding:0 20px;font-size:16px}.brand .mk{width:26px;height:26px;border-radius:7px;background:var(--ink);color:#fff;display:grid;place-items:center}.brand .mk svg{width:16px;height:16px}
.sf{display:flex;align-items:center;gap:10px;max-width:480px;width:100%;height:40px;padding:0 12px;border:1px solid var(--line2);border-radius:8px;background:var(--side);color:var(--mute);font-size:15px;cursor:pointer;margin-left:24px;text-align:left}
.sf span{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sf kbd{font-size:12px;border:1px solid var(--line2);border-radius:5px;padding:1px 6px;background:#fff;color:var(--sub)}
.tn{display:flex;gap:2px;padding:0 20px;align-items:center}.tn a{padding:7px 11px;border-radius:7px;font-size:15px;font-weight:600;color:var(--sub)}.tn a:hover{background:var(--side);color:var(--ink)}.tn a[aria-current]{color:var(--ac)}
.tn a.st{background:var(--ac);color:#fff;margin-left:8px}.mtg{display:none}
.shell{display:grid;grid-template-columns:260px minmax(0,1fr)}
.side{border-right:1px solid var(--line);background:var(--side);position:sticky;top:60px;height:calc(100vh - 60px);overflow:auto;padding:20px 12px 40px;font-size:14.5px}
.side h4{font-size:12px;font-weight:700;color:var(--mute);letter-spacing:.04em;margin:20px 10px 6px}.side h4:first-child{margin-top:0}
.side a{display:flex;gap:10px;align-items:center;padding:6px 10px;border-radius:7px;color:var(--sub)}.side a:hover{background:#F0EFEB;color:var(--ink)}.side a.on{background:var(--ac-s);color:var(--ac);font-weight:700}
.side a>svg{width:17px;height:17px;color:var(--mute)}.side a.on>svg{color:var(--ac)}.side .sub{margin-left:20px;border-left:1px solid var(--line2);padding-left:6px}.side .sub a{font-size:14px;padding:4px 10px}.side .n{font-family:"JetBrains Mono",monospace;font-size:12px;color:var(--mute)}
.main{padding:40px 48px 80px;max-width:1180px}
h1{font-size:40px;line-height:1.2;font-weight:800;letter-spacing:-.025em}h2{font-size:24px;line-height:1.3;font-weight:800;letter-spacing:-.015em}h3{font-size:17px;font-weight:700;line-height:1.35}
.th{display:flex;gap:16px;align-items:center}.lede{font-size:18px;color:var(--sub);margin-top:10px;max-width:680px}
.sec{margin-top:56px}.sh{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:16px}.sh a{font-size:14px;font-weight:600;color:var(--ac);display:flex;gap:4px;align-items:center}.sh a svg{width:16px;height:16px}
.crumb{display:flex;gap:6px;align-items:center;font-size:14px;color:var(--mute);flex-wrap:wrap;margin-bottom:14px}.crumb svg{width:14px;height:14px}.crumb a:hover{color:var(--ac)}
code{font-family:"JetBrains Mono","D2Coding Hangul",monospace;font-size:.86em;background:var(--code);padding:1px 5px;border-radius:4px}
/* 큰 타일 */
.tiles{display:grid;gap:12px}.t6{grid-template-columns:repeat(6,minmax(0,1fr))}.t5{grid-template-columns:repeat(5,minmax(0,1fr))}.t4{grid-template-columns:repeat(4,minmax(0,1fr))}.t3{grid-template-columns:repeat(3,minmax(0,1fr))}
.tile{display:flex;flex-direction:column;gap:12px;border:1px solid var(--line);border-radius:14px;padding:18px;background:#fff;transition:border-color .15s}.tile:hover{border-color:var(--ac)}.tile b{font-size:16px;line-height:1.35}.tile small{color:var(--mute);font-size:13px}
.tile.c{align-items:center;text-align:center;padding:22px 12px}
.stg .no{font-family:"JetBrains Mono",monospace;font-size:13px;color:var(--mute)}.stg{position:relative}
.num{font-size:34px;font-weight:800;letter-spacing:-.02em;line-height:1}
.lc{display:block;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#fff}.lc:hover{border-color:var(--ac)}.lc img.cv{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;background:#1D2330}
.lc .bd{padding:12px 14px 14px;display:flex;flex-direction:column;gap:8px}.lc b{font-size:15.5px;line-height:1.35}.lc small{color:var(--mute);font-size:13px}
.search{display:flex;align-items:center;gap:12px;height:56px;padding:0 18px;border:1px solid var(--line2);border-radius:12px;font-size:17px;color:var(--mute);margin-top:22px;cursor:pointer;background:#fff;width:100%;max-width:620px;text-align:left}.search span{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.search kbd{font-size:13px;border:1px solid var(--line2);border-radius:6px;padding:2px 8px}
details.more{margin-top:14px;max-width:760px}details.more summary{cursor:pointer;font-size:14.5px;font-weight:600;color:var(--sub);display:inline-flex;gap:6px;align-items:center;list-style:none}details.more summary::-webkit-details-marker{display:none}
details.more summary svg{width:16px;height:16px;transition:transform .15s}details.more[open] summary svg{transform:rotate(90deg)}details.more>div{margin-top:10px;color:var(--sub);font-size:15px}details.more>div p{margin:6px 0}
.news{list-style:none;margin:0;padding:0}.news li{display:flex;gap:14px;padding:9px 0;border-top:1px solid var(--line);font-size:15px;align-items:center}.news time{font-family:"JetBrains Mono",monospace;font-size:13px;color:var(--mute);flex:none}
.badge{font-size:12px;font-weight:700;color:var(--sub);border:1px solid var(--line2);border-radius:5px;padding:0 6px;flex:none}.badge.r{color:var(--ac);border-color:#C9D7F5;background:var(--ac-s)}
.ft{border-top:1px solid var(--line);padding:24px 48px 40px;font-size:13px;color:var(--mute)}.ft b{color:var(--sub)}.ft p{margin-top:3px}.ft a{text-decoration:underline}
/* 로드맵 */
.stage{margin-top:44px;padding-top:28px;border-top:1px solid var(--line)}.stage:first-of-type{border:0;padding-top:0}
.tp{display:flex;flex-direction:column;gap:10px;border:1px solid var(--line);border-radius:12px;padding:14px 16px;background:#fff}.tp:hover{border-color:var(--ac)}.tp .hd{display:flex;gap:10px;align-items:center}.tp b{font-size:15px;line-height:1.35}.tp .soon{font-size:12.5px;color:var(--mute)}
/* 주제 */
.ask{margin-top:16px;font-size:20px;font-weight:600;color:var(--ink);max-width:760px;padding-left:16px;border-left:4px solid var(--ac)}
.know{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.kn{display:flex;justify-content:space-between;gap:14px;align-items:center;border:1px solid var(--line);border-radius:12px;padding:12px 14px;background:#fff}.kn span{font-size:15px;line-height:1.4}
.chip{display:inline-flex;gap:6px;align-items:center;font-family:"JetBrains Mono",monospace;font-size:13px;font-weight:600;padding:3px 9px 3px 5px;border-radius:8px;background:var(--side);border:1px solid var(--line)}.chip:hover{border-color:var(--ac)}.chips{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end;flex:none;max-width:52%}
.chips em{font-style:normal;font-size:13px;color:var(--mute);white-space:nowrap}
.doc details{border:1px solid var(--line);border-radius:12px;margin-top:10px;background:#fff}.doc summary{cursor:pointer;padding:14px 18px;font-weight:700;font-size:16px;display:flex;justify-content:space-between;align-items:center;list-style:none}.doc summary::-webkit-details-marker{display:none}
.doc summary svg{width:18px;height:18px;color:var(--mute);transition:transform .15s}.doc details[open] summary svg{transform:rotate(180deg)}.doc .in{padding:0 18px 16px;font-size:15.5px;max-width:800px}
.doc .in h3{margin:18px 0 6px}.doc .in p{margin:8px 0}.doc .in ul,.doc .in ol{padding-left:22px}.doc .in a{color:var(--ac)}.tw{overflow-x:auto;border:1px solid var(--line);border-radius:10px;margin:12px 0}.tw table{border-collapse:collapse;width:100%;font-size:14.5px}.tw th,.tw td{text-align:left;vertical-align:top;padding:9px 12px;border-bottom:1px solid var(--line)}.tw th{background:var(--side)}.tw tr:last-child td{border:0}
.src{display:flex;gap:16px;flex-wrap:wrap;font-size:13px;color:var(--mute);margin-top:16px}.src a,.src span{display:flex;gap:6px;align-items:center}.src svg{width:15px;height:15px}.src a:hover{color:var(--ac)}
.next{display:flex;justify-content:flex-end;margin-top:36px}.next a{display:flex;gap:14px;align-items:center;border:1px solid var(--line);border-radius:14px;padding:14px 18px;min-width:280px}.next a:hover{border-color:var(--ac)}.next small{display:block;color:var(--mute);font-size:13px}.next b{font-size:17px}
/* 챕터 */
.player{position:relative;aspect-ratio:16/9;border-radius:14px;overflow:hidden;background:#1D2330;margin-top:24px;cursor:pointer}.player img{width:100%;height:100%;object-fit:cover;display:block}.player iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.player .play{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);display:flex;gap:10px;align-items:center;height:60px;padding:0 28px;border-radius:30px;background:#fff;color:var(--ink);font-weight:800;box-shadow:0 8px 24px rgba(0,0,0,.3);border:0;font-size:18px;cursor:pointer}.player .play svg{width:22px;height:22px;fill:currentColor}
.acts{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}.acts a{display:flex;align-items:center;gap:8px;height:40px;padding:0 16px;border:1px solid var(--line2);border-radius:10px;font-weight:600;font-size:15px}.acts a:hover{border-color:var(--ac);color:var(--ac)}.acts svg{width:17px;height:17px}
.part{display:block;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff}.part:hover{border-color:var(--ac)}.part img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;border-bottom:1px solid var(--line)}.part div{padding:10px 12px;display:flex;justify-content:space-between;gap:8px;align-items:baseline}.part b{font-size:14.5px;line-height:1.35}.part small{font-family:"JetBrains Mono",monospace;font-size:12px;color:var(--mute);white-space:nowrap}
.goals{list-style:none;padding:0;margin:0;display:grid;gap:6px}.goals li{display:flex;gap:10px;align-items:flex-start;font-size:15px}.goals svg{width:18px;height:18px;color:#1F7A4D;margin-top:3px;flex:none}
.use{display:flex;gap:16px;align-items:center;border:1px solid #C9D7F5;background:var(--ac-s);border-radius:14px;padding:16px 18px}.use b{font-size:17px}.use small{display:block;color:var(--sub);font-size:14px}.use .go{margin-left:auto;color:var(--ac)}
.pn{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:40px}.pn a{display:flex;gap:14px;align-items:center;border:1px solid var(--line);border-radius:14px;padding:12px 16px}.pn a:hover{border-color:var(--ac)}.pn img.cv{width:96px;aspect-ratio:16/9;object-fit:cover;border-radius:6px}.pn small{display:block;color:var(--mute);font-size:13px}.pn b{font-size:15.5px}.pn .r{flex-direction:row-reverse;text-align:right}
/* 사례 */
.case{display:flex;flex-direction:column;gap:12px;border:1px solid var(--line);border-radius:14px;padding:18px;background:#fff}.case:hover{border-color:var(--ac)}.case .hd{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}.case b{font-size:16px;line-height:1.4}
.case .ft2{display:flex;justify-content:space-between;align-items:center;margin-top:auto;font-size:13px;color:var(--mute)}
.diff{display:inline-flex;gap:3px;align-items:center}.diff i{width:16px;height:6px;border-radius:3px;background:var(--line2);display:block}.diff i.on{background:var(--ink)}
.run{display:inline-flex;gap:4px;align-items:center;font-size:12px;font-weight:700;color:#1F7A4D;background:#E8F4EE;border-radius:6px;padding:2px 8px;white-space:nowrap}.run svg{width:12px;height:12px}
.fchips{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}.fchips button{display:flex;gap:6px;align-items:center;height:38px;padding:0 14px;border-radius:19px;border:1px solid var(--line2);background:#fff;font-size:14.5px;cursor:pointer}.fchips button svg{width:16px;height:16px}.fchips button[aria-pressed=true]{background:var(--ink);color:#fff;border-color:var(--ink)}
.libt{display:flex;gap:12px;align-items:center}.libt .num{font-size:26px}.tile.on{border-color:var(--ac);background:var(--ac-s)}
${DLG_CSS({ scrim: "rgba(29,35,48,.4)", bg: "#fff", ink: "#1D2330", line: "#EAE9E6", sub: "#5F6675", r: "12px", hover: "#F4F3F0" })}
@media (max-width:1240px){.t6{grid-template-columns:repeat(3,minmax(0,1fr))}.t5{grid-template-columns:repeat(3,minmax(0,1fr))}.tn a:not(.st){display:none}.main{padding:32px 32px 72px}}
@media (max-width:860px){.top{grid-template-columns:auto minmax(0,1fr) auto}.side{display:none}.shell{grid-template-columns:minmax(0,1fr)}.sf{margin-left:0}.sf kbd,.brand b{display:none}.mtg{display:grid;place-items:center;width:40px;height:40px;margin-left:8px;border:0;background:none}
.main{padding:24px 16px 64px}h1{font-size:30px}.ft{padding:24px 16px 40px}.t4,.t3,.know{grid-template-columns:repeat(2,minmax(0,1fr))}.tn{padding:0 12px 0 8px}.brand{padding:0 0 0 12px}.pn{grid-template-columns:1fr}.pn img.cv{width:72px}}
@media (max-width:560px){.t6,.t5{grid-template-columns:repeat(2,minmax(0,1fr))}.t4,.t3,.know{grid-template-columns:minmax(0,1fr)}.kn{flex-direction:column;align-items:flex-start}.chips{justify-content:flex-start;max-width:none}.next a{min-width:0;width:100%}.ask{font-size:18px}.lede{font-size:16px}}`;

const kit0 = kitFor();
const kit = { dlg: kit0.dlg, js: kit0.js + `<script>document.querySelectorAll('[data-player]').forEach(p=>p.onclick=()=>{if(p.querySelector('iframe'))return;p.innerHTML='<iframe src="'+p.dataset.player+'" title="슬라이드" allow="fullscreen"></iframe>'});
document.querySelectorAll('.fchips button').forEach(o=>o.onclick=()=>{document.querySelectorAll('.fchips button').forEach(x=>x.setAttribute('aria-pressed',x===o));const a=o.dataset.a;document.querySelectorAll('.case').forEach(c=>c.hidden=a!=='all'&&c.dataset.a!==a)});</script>` };
const side = (on) => `<nav class="side" aria-label="전체 목차">
<h4>시작</h4><a href="home.html"${on === "home" ? ' class="on"' : ""}>${i("signpost")}처음 오셨나요</a><a href="#">${i("book-a")}용어 사전</a>
<h4>로드맵</h4>${S.stages.map((s) => `<a href="roadmap.html">${i(STAGE_IC[s.no])}${esc(stageShort(s.title))}</a>${s.no === 2 && on === "topic" ? `<div class="sub">${s.areas.map((a, n) => `<a href="topic.html"${n === 0 ? ' class="on"' : ""}>${esc(a.t)}</a>`).join("")}</div>` : ""}`).join("")}
<h4>강의</h4>${lecStages.map((s) => `<a href="chapter.html">${lg(s.logos[0], 18)}${esc(s.title)}</a>${on === "chapter" && s.no === 4 ? `<div class="sub">${s.list.map((c) => `<a href="chapter.html"${c.no === "36" ? ' class="on"' : ""}><span class="n">${c.no}</span>${esc(short(c.title))}</a>`).join("")}</div>` : ""}`).join("")}<a href="chapter.html">${i("lightbulb")}꿀팁</a>
<h4>사례와 자료</h4>${LIB.map(([k, t]) => `<a href="cases.html"${on === "cases" && k === "cases" ? ' class="on"' : ""}>${i(LIB_IC[k])}${t}</a>`).join("")}
<h4>그 밖</h4><a href="home.html#news">${i("megaphone")}소식</a><a href="#">${i("info")}이 사이트에 대해</a></nav>`;
const top = (cur) => `<header class="top"><a class="brand" href="home.html"><span class="mk">${i("book-open")}</span><b>${D.NAME}</b></a>
<button class="sf" data-search>${i("search")}<span>주제, 챕터, 명령어, 사례 찾기</span><kbd>/</kbd></button>
<nav class="tn" aria-label="메뉴">${MENU.map(([k, t, h]) => `<a href="${h}"${k === cur ? ' aria-current="page"' : ""}>${t}</a>`).join("")}<a class="st" href="home.html#start">시작하기</a><button class="mtg" aria-label="전체 목차">${i("menu")}</button></nav></header>`;
const foot = `<footer class="ft"><b>${FOOT}</b>${LIC.map((l) => `<p>${l}</p>`).join("")}<p>로고: devicon(MIT), Simple Icons(CC0). 각 로고의 상표는 그 소유자에게 있어요. 고칠 곳과 질문: <a href="mailto:${D.CONTACT}">${D.CONTACT}</a></p></footer>`;
const crumb = (xs) => `<nav class="crumb" aria-label="현재 위치">${xs.map(([t, h], n) => (h ? `<a href="${h}">${t}</a>` : `<span>${t}</span>`) + (n < xs.length - 1 ? i("chevron-right") : "")).join("")}</nav>`;
const chips = (nos) => (nos.length ? `<span class="chips">${nos.map((n) => `<a class="chip" href="chapter.html" title="${esc(byNo[n].title)}">${lg(byNo[n].logos[0], 18)}${n}</a>`).join("")}</span>` : `<span class="chips"><em>강의 준비 중</em></span>`);
const more = (label, body) => `<details class="more"><summary>${i("chevron-right")}${label}</summary><div>${body}</div></details>`;
const page = (title, cur, on, body) => html(title, css, `${top(cur)}<div class="shell">${side(on)}<div><main class="main">${body}</main>${foot}</div></div>`, kit);
const lecCard = (n, big) => { const c = byNo[n]; return `<a class="lc" href="chapter.html"><img class="cv" src="${cover(n)}" alt="" loading="lazy"><div class="bd">${lgs(c.logos, big ? 28 : 24)}<b>${n} ${esc(short(c.title))}</b></div></a>`; };

/* 홈 */
const home = page(D.NAME, "", "home", `<h1>AX 엔지니어 핸드북</h1><p class="lede">AX 엔지니어가 되는 길과 그 길에 필요한 기초 강의를 한곳에 모았어요.</p>
<button class="search" data-search>${i("search")}<span>트랜잭션, MCP, 법인카드 정산처럼 찾아요</span><kbd>/</kbd></button>
${more("AX 엔지니어는 어떤 일을 하나요?", `<p>${esc(S.defn)}</p>`)}
<section class="sec" id="start"><div class="sh"><h2>어디서 시작할까요?</h2></div><div class="tiles t6">${START.map(([ic, t, h]) => `<a class="tile c" href="${h}">${ict(ic, "lg2")}<b>${t}</b></a>`).join("")}</div></section>
<section class="sec"><div class="sh"><h2>로드맵 5단계</h2><a href="roadmap.html">전체 보기 ${i("arrow-right")}</a></div><div class="tiles t5">${S.stages.map((s) => `<a class="tile stg" href="roadmap.html"><span class="no">${s.no}단계</span>${ict(STAGE_IC[s.no], "lg2")}<b>${esc(stageShort(s.title))}</b><small>${stageCount(s)}</small></a>`).join("")}</div></section>
<section class="sec"><div class="sh"><h2>기초 강의</h2><a href="chapter.html">${D.chapters.length}챕터 모두 ${i("arrow-right")}</a></div><div class="tiles t5">${lecStages.map((s) => `<a class="lc" href="chapter.html"><img class="cv" src="${cover(s.from)}" alt="" loading="lazy"><div class="bd">${lgs(s.logos.slice(0, 4), 26)}<b>${esc(s.title)}</b><small>${s.from}–${s.to} · ${s.list.length}챕터</small></div></a>`).join("")}</div></section>
<section class="sec"><div class="sh"><h2>사례와 자료</h2></div><div class="tiles t5">${LIB.map(([k, t, n]) => `<a class="tile" href="cases.html">${ict(LIB_IC[k])}<span class="num">${n}</span><b>${t}</b></a>`).join("")}</div></section>
<section class="sec" id="news"><div class="sh"><h2 style="font-size:18px">소식</h2></div><ul class="news">${NEWS.slice(0, 3).map(([d, k, t]) => `<li><time>${d}</time><span class="badge ${k === "로드맵" ? "r" : ""}">${k}</span><span>${t}</span></li>`).join("")}</ul></section>`);

/* 로드맵 */
const roadmap = page("로드맵 · " + D.NAME, "roadmap", "roadmap", `${crumb([["홈", "home.html"], ["로드맵"]])}<div class="th">${ict("route", "lg2")}<h1>AX 엔지니어 로드맵</h1></div><p class="lede">다섯 단계를 차례로 따라가요. 주제 카드의 로고는 먼저 익힐 기초 강의예요.</p>
${S.stages.map((s) => `<section class="stage"><div class="th">${ict(STAGE_IC[s.no])}<div><span style="font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--mute)">${s.no}단계 · ${stageCount(s)}</span><h2>${esc(s.title)}</h2></div></div>
<div class="tiles ${s.no === 5 ? "t3" : "t4"}" style="margin-top:16px">${stageTopics(s).map((t, n) => { const id = s.areas?.[n]?.id; const ls = id ? AREA_LINKS[id] : s.no === 4 && n === 0 ? ["09", "10", "44"] : s.no === 3 && n === 3 ? ["32", "45", "46"] : []; const icn = id ? AREA_IC[id] : s.no === 5 ? CASE_IC[S.cases[n].area] : null;
  return `<a class="tp" href="topic.html"><span class="hd">${icn ? ict(icn, s.no === 5 ? "sm n" : "sm") : `<span class="ict sm n" style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700">${s.no}.${n + 1}</span>`}<b>${esc(t)}</b></span>${ls.length ? lgs([...new Set(ls.map((x) => byNo[x].logos[0]))], 22) : id ? `<span class="soon">강의 준비 중</span>` : ""}</a>`; }).join("")}</div>
${more("단계 설명" + (s.checks.length ? "과 점검 질문" : ""), `<p>${esc(s.lede)}</p>${s.checks.map((c) => `<p>${i("circle-check")} ${esc(c)}</p>`).join("")}`)}</section>`).join("")}`);

/* 로드맵 주제 */
const T = TOPIC;
const topic = page(T.title + " · 로드맵", "roadmap", "topic", `${crumb([["로드맵", "roadmap.html"], ["2. " + stageShort(T.stage.title), "roadmap.html"], [T.title]])}<div class="th">${ict(AREA_IC[T.area.id], "lg2")}<h1>${esc(T.title)}</h1></div>
<p class="ask">${esc(T.area.q)}</p>${more("왜 필요한가", `<p>${esc(T.why)}</p>`)}
<section class="sec"><div class="sh"><h2>먼저 익힐 기초 강의</h2><span style="font-size:14px;color:var(--mute)">${T.lec.length}챕터</span></div><div class="tiles t4">${T.lec.map((n) => lecCard(n)).join("")}</div></section>
<section class="sec"><div class="sh"><h2>알아야 할 것</h2></div><div class="know">${T.know.map((k) => `<div class="kn"><span>${esc(k.t)}</span>${chips(k.lec)}</div>`).join("")}</div></section>
<section class="sec doc"><div class="sh"><h2>로드맵 문서</h2><a href="${D.GH(T.src)}">원문 ${i("external-link")}</a></div>${T.body.o.split(/(?=<h2 id=)/).filter((x) => x.startsWith("<h2")).map((x) => { const m = /<h2 id="[^"]+">([^<]+)<\/h2>([\s\S]*)/.exec(x); return `<details><summary>${m[1]}${i("chevron-down")}</summary><div class="in">${m[2]}</div></details>`; }).join("")}
<p class="src"><span>${i("git-branch")}ax-engineer-roadmap ${S.version}</span><a href="${D.GH(T.src)}">${i("pencil")}고치기 제안</a></p></section>
<div class="next"><a href="topic.html">${ict(AREA_IC[T.next.id])}<span><small>다음 주제</small><b>${esc(T.next.t)}</b></span></a></div>`);

/* 강의 챕터 */
const c = CH.c;
const PART_IMG = (a) => (a === 1 ? cover(c.no) : `../shared/slides36/${String(a).padStart(2, "0")}.jpg`);
const chapter = page(c.title + " · 강의", "lectures", "chapter", `${crumb([["강의", "chapter.html"], [`${c.stage}. ${c.stageTitle}`, "chapter.html"], [`${c.no}`]])}<div class="th">${lg(c.logos[0], 56)}<div><span style="font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--mute)">${c.no} · ${c.track} · ${c.level}</span><h1>${esc(short(c.title))}</h1></div></div>
<p class="lede">${esc(c.goal.replace(/`/g, ""))}</p>
<div class="player" data-player="${CH.deck}"><img src="${cover(c.no)}" alt="${esc(c.title)} 표지"><button class="play" type="button">${i("play")}슬라이드 보기</button></div>
<div class="acts"><a href="${CH.deck}">${i("presentation")}크게 보기</a><a href="${CH.pdf}">${i("download")}PDF 받기</a><a href="#">${i("square-terminal")}명령어 요약</a><a href="#">${i("triangle-alert")}문제 해결</a></div>
<section class="sec"><div class="sh"><h2>구성</h2><span style="font-size:14px;color:var(--mute)">${CH.slides.length}쪽 · 파트 ${CH.parts.length}개</span></div><div class="tiles t4">${CH.parts.map((p) => `<a class="part" href="#"><img src="${PART_IMG(p.a)}" alt="" loading="lazy"><div><b>${esc(p.p.replace(/^\d+\. /, ""))}</b><small>${p.a}${p.b > p.a ? "–" + p.b : ""}</small></div></a>`).join("")}</div>
${more(`배우는 것 ${CH.goals.length}가지`, `<ul class="goals">${CH.goals.map((g) => `<li>${i("circle-check")}<span>${esc(g).replace(/`([^`]+)`/g, "<code>$1</code>")}</span></li>`).join("")}</ul>`)}</section>
<section class="sec"><a class="use" href="topic.html">${ict("plug", "lg2")}<span><small>이 챕터를 쓰는 로드맵 주제</small><b>2단계 · ${esc(CH.used[0])}</b></span><span class="go">${i("arrow-right")}</span></a></section>
<div class="pn"><a href="chapter.html"><img class="cv" src="${cover(CH.prev.no)}" alt=""><span><small>이전</small><b>${CH.prev.no} ${esc(short(CH.prev.title))}</b></span></a><a class="r" href="chapter.html"><img class="cv" src="${cover(CH.next.no)}" alt=""><span><small>다음</small><b>${CH.next.no} ${esc(short(CH.next.title))}</b></span></a></div>`);

/* 사례와 자료 */
const cases = page("사례와 자료 · " + D.NAME, "library", "cases", `${crumb([["사례와 자료", "cases.html"], ["업무 사례"]])}<div class="th">${ict("briefcase", "lg2")}<h1>업무 사례</h1></div><p class="lede">업무 하나를 처음부터 끝까지 설계해 본 사례예요. 실제 회사의 성과가 아니라 연습용 설계예요.</p>
<div class="tiles t5" style="margin-top:24px">${LIB.map(([k, t, n]) => `<a class="tile${k === "cases" ? " on" : ""}" href="cases.html"><span class="libt">${ict(LIB_IC[k], "sm")}<span class="num">${n}</span></span><b>${t}</b></a>`).join("")}</div>
<div class="fchips" role="group" aria-label="업무 분야"><button aria-pressed="true" data-a="all">전체 ${S.cases.length}</button>${AREAS.map((a) => `<button aria-pressed="false" data-a="${esc(a)}">${i(CASE_IC[a])}${esc(a)}</button>`).join("")}</div>
<div class="tiles t3">${S.cases.map((x) => `<a class="case" href="cases.html" data-a="${esc(x.area)}"><span class="hd">${ict(CASE_IC[x.area], "n")}${/재현 가능/.test(x.ev) ? `<span class="run">${i("play")}실행 예제</span>` : ""}</span><b>${esc(x.t)}</b>
<span class="ft2"><span>${esc(x.area)}</span><span class="diff" title="난이도 ${x.diff} / 5">${[1, 2, 3, 4, 5].map((k) => `<i class="${k <= x.diff ? "on" : ""}"></i>`).join("")}</span></span></a>`).join("")}</div>`);

for (const [f, h] of Object.entries({ home, roadmap, topic, chapter, cases })) write("v16", f + ".html", h);
console.log("v16 ok");
