// 시안 v15 · 핸드북에 그림 더하기. v12 틀(왼쪽 목차, 본문, 쪽 안 목차, 찾기)은 그대로 두고 아이콘, 도구 로고, 덱 표지, 연결 그림을 더해요.
// 꾸밈 규칙: 아이콘은 뜻이 있는 자리(단계, 영역, 자료 묶음, 업무 분야)에만, 색은 로드맵 파랑 하나와 도구 로고 고유색만 써요.
import * as D from "../plan/data.mjs";
const { i, esc, S, byNo, short, stageShort, TOPIC, CH, LIB, NEWS, MENU, FOOT, LIC, html, DLG_CSS, kitFor, AREAS, stageTopics, stageCount, STAGE_LINKS, AREA_LINKS, SOON, lecStages } = D;
import { write, tile, LOGO, IC } from "../lib.mjs";

/* 뜻이 있는 자리의 아이콘 */
const STAGE_IC = { 1: "compass", 2: "layers", 3: "workflow", 4: "flag", 5: "building-2" };
const AREA_IC = { "software-and-api": "plug", "llm-foundations": "brain", "agent-systems": "bot", "tools-and-mcp": "wrench", "evaluation-and-testing": "gauge", "production-operations": "activity", "security-and-privacy": "shield-check" };
const LIB_IC = { cases: "briefcase", public: "file-check-2", failures: "triangle-alert", templates: "clipboard-check", jobs: "chart-column" };
const CASE_IC = { "고객·매출": "messages-square", "사람·협업": "users", "재무·구매": "receipt", "데이터·운영": "database", "공통 기능·운영": "layers" };
const START_IC = ["square-terminal", "code-xml", "briefcase", "book-a", "play", "presentation"];
const cover = (n) => `../shared/covers/${n}.jpg`;
const ict = (n, cls = "") => `<span class="ict ${cls}">${i(n)}</span>`;
const logos = (ks, sz = 22) => `<span class="lgs">${ks.map((k) => tile(k, sz)).join("")}</span>`;

const css = `:root{--bg:#fff;--side:#FAFAF9;--ink:#1D2330;--sub:#5F6675;--mute:#9298A4;--line:#EAE9E6;--line2:#D9D7D2;--ac:#2459C9;--ac-s:#EEF3FD;--code:#F4F3F0}
body{background:var(--bg);color:var(--ink);font-size:16px;line-height:1.65}
.logo-tile{width:var(--sz);height:var(--sz);border-radius:calc(var(--sz) / 4);background:#fff;box-shadow:inset 0 0 0 1px var(--line2);display:grid;place-items:center;flex:none}.logo-tile svg{width:62%;height:62%}
.lgs{display:inline-flex;gap:4px;flex-wrap:wrap}
.ict{width:36px;height:36px;border-radius:10px;background:var(--ac-s);color:var(--ac);display:grid;place-items:center;flex:none}.ict svg{width:20px;height:20px}
.ict.sm{width:26px;height:26px;border-radius:7px}.ict.sm svg{width:15px;height:15px}.ict.lg{width:52px;height:52px;border-radius:14px}.ict.lg svg{width:28px;height:28px;stroke-width:1.6}
.ict.n{background:var(--code);color:var(--ink)}
.top{height:60px;border-bottom:1px solid var(--line);display:grid;grid-template-columns:280px minmax(0,1fr) auto;align-items:center;position:sticky;top:0;background:#fff;z-index:5}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;padding:0 20px;font-size:16px}.brand .mk{width:26px;height:26px;border-radius:7px;background:var(--ink);color:#fff;display:grid;place-items:center}.brand .mk svg{width:16px;height:16px}
.sf{display:flex;align-items:center;gap:10px;max-width:520px;width:100%;height:40px;padding:0 12px;border:1px solid var(--line2);border-radius:8px;background:var(--side);color:var(--mute);font-size:15px;cursor:pointer;margin-left:24px;text-align:left}
.sf span{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sf kbd{font-size:12px;border:1px solid var(--line2);border-radius:5px;padding:1px 6px;background:#fff;color:var(--sub)}
.tn{display:flex;gap:2px;padding:0 20px;align-items:center}.tn a{padding:7px 11px;border-radius:7px;font-size:15px;font-weight:600;color:var(--sub)}.tn a:hover{background:var(--side);color:var(--ink)}.tn a[aria-current]{color:var(--ac)}
.tn a.st{background:var(--ac);color:#fff;margin-left:8px}.mtg{display:none}
.shell{display:grid;grid-template-columns:280px minmax(0,1fr)}
.side{border-right:1px solid var(--line);background:var(--side);position:sticky;top:60px;height:calc(100vh - 60px);overflow:auto;padding:20px 12px 40px;font-size:14.5px}
.side h4{font-size:12px;font-weight:700;color:var(--mute);letter-spacing:.04em;margin:22px 10px 6px}.side h4:first-child{margin-top:0}
.side a{display:flex;gap:9px;align-items:center;padding:5px 10px;border-radius:6px;color:var(--sub);line-height:1.45}.side a:hover{background:#F0EFEB;color:var(--ink)}.side a.on{background:var(--ac-s);color:var(--ac);font-weight:700}
.side a>svg{width:16px;height:16px;color:var(--mute)}.side a.on>svg{color:var(--ac)}.side a .n{font-family:"JetBrains Mono",monospace;font-size:12px;color:var(--mute);min-width:18px}
.side .sub{margin-left:18px;border-left:1px solid var(--line2);padding-left:6px}.side .sub a{font-size:14px}.side a .c{margin-left:auto;font-size:12px;color:var(--mute)}
.main{display:grid;grid-template-columns:minmax(0,1fr) 220px;gap:48px;padding:36px 48px 80px;max-width:1240px}.main.wide{grid-template-columns:minmax(0,1fr)}
.crumb{display:flex;gap:6px;align-items:center;font-size:14px;color:var(--mute);flex-wrap:wrap}.crumb a:hover{color:var(--ac)}.crumb svg{width:14px;height:14px}
h1{font-size:36px;line-height:1.25;font-weight:800;letter-spacing:-.02em}h2{font-size:24px;line-height:1.35;font-weight:800;letter-spacing:-.01em}h3{font-size:17px;font-weight:700}
.th{display:flex;gap:16px;align-items:center;margin-top:12px}
.desc{font-size:18px;color:var(--sub);margin-top:10px;max-width:760px}.metal{display:flex;gap:16px;flex-wrap:wrap;margin-top:14px;font-size:13px;color:var(--mute)}.metal span,.metal a{display:flex;gap:6px;align-items:center}.metal svg{width:15px;height:15px}.metal a:hover{color:var(--ac)}
.mono,code{font-family:"JetBrains Mono","D2Coding Hangul",monospace}code{font-size:.86em;background:var(--code);padding:1px 5px;border-radius:4px}
.call{display:grid;grid-template-columns:36px minmax(0,1fr);gap:14px;border:1px solid #C9D7F5;background:var(--ac-s);border-radius:12px;padding:16px 18px;margin-top:24px}.call .ict{background:#fff}.call h3{font-size:16px}.call p{font-size:14.5px;color:var(--sub)}
table{border-collapse:collapse;width:100%;font-size:15px}.tbl{border:1px solid var(--line);border-radius:10px;overflow:hidden;margin-top:14px}.tbl th,.tbl td{text-align:left;vertical-align:middle;padding:10px 14px;border-bottom:1px solid var(--line)}
.tbl tr:last-child td{border-bottom:0}.tbl th{background:var(--side);font-size:13px;color:var(--sub);font-weight:700}.tbl td.n{font-family:"JetBrains Mono",monospace;font-size:13px;color:var(--sub);width:48px}.tbl a{color:var(--ac)}.tbl a:hover{text-decoration:underline}
.tbl .r{text-align:right;font-variant-numeric:tabular-nums}.tbl small{color:var(--mute)}.tbl .tt{display:flex;gap:10px;align-items:center}
.prose{max-width:780px}.prose h2{margin:44px 0 10px;padding-top:12px;border-top:1px solid var(--line)}.prose h3{margin:24px 0 6px}.prose p{margin:10px 0}.prose ul,.prose ol{padding-left:22px}.prose li{margin:4px 0}.prose a{color:var(--ac)}.prose a:hover{text-decoration:underline}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:10px;margin:14px 0}.tw th,.tw td{text-align:left;vertical-align:top;padding:9px 12px;border-bottom:1px solid var(--line)}.tw th{background:var(--side);font-size:13px}.tw tr:last-child td{border:0}
.lec{display:inline-flex;gap:4px;flex-wrap:wrap}.lec a{display:inline-flex;gap:5px;align-items:center;font-family:"JetBrains Mono",monospace;font-size:12px;padding:2px 7px 2px 3px;border-radius:6px;background:#fff;box-shadow:inset 0 0 0 1px var(--line2);color:var(--ink)}.lec a:hover{box-shadow:inset 0 0 0 1px var(--ac);color:var(--ac)}
.lec a .logo-tile{box-shadow:none}.lec em{font-style:normal;font-size:13px;color:var(--mute)}
.otp{position:sticky;top:96px;align-self:start;font-size:13.5px}.otp h4{font-size:12px;color:var(--mute);font-weight:700;letter-spacing:.04em;margin-bottom:8px}.otp a{display:block;padding:4px 0;color:var(--sub)}.otp a:hover{color:var(--ac)}.otp a.on{color:var(--ac);font-weight:700}
.otp .blk{margin-top:22px;padding-top:16px;border-top:1px solid var(--line)}.otp .rel{display:flex;gap:8px;align-items:flex-start;padding:5px 0}.otp .rel svg{width:15px;height:15px;margin-top:3px;flex:none}
.pn{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:48px}.pn a{display:flex;gap:12px;align-items:center;border:1px solid var(--line);border-radius:10px;padding:12px 16px}.pn a:hover{border-color:var(--ac)}.pn small{display:block;font-size:13px;color:var(--mute)}.pn b{color:var(--ac)}.pn .r{grid-column:2;justify-content:flex-end;text-align:right}
.edit{display:flex;gap:6px;align-items:center;font-size:13px;color:var(--mute);margin-top:28px}.edit svg{width:15px;height:15px}.edit a{color:var(--sub);text-decoration:underline}
/* 홈 */
.hero{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,540px);gap:40px;align-items:center}
.bigs{display:flex;align-items:center;gap:12px;height:56px;padding:0 18px;border:1px solid var(--line2);border-radius:12px;font-size:17px;color:var(--mute);margin-top:24px;cursor:pointer;background:#fff;width:100%;text-align:left;box-shadow:0 1px 2px rgba(0,0,0,.04)}.bigs span{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bigs kbd{font-size:13px;border:1px solid var(--line2);border-radius:6px;padding:2px 8px;color:var(--sub)}.hint{font-size:13px;color:var(--mute);margin-top:10px}.hint code{font-size:12px}
.map{border:1px solid var(--line);border-radius:14px;background:var(--side);padding:14px 16px 10px}.map figcaption{font-size:12.5px;color:var(--mute);margin-top:4px}.map svg{width:100%;height:auto}
.ix{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:40px}.ixb{border:1px solid var(--line);border-radius:12px;padding:18px 20px}.ixh{display:flex;gap:12px;align-items:center}.ixh h2{font-size:17px}.ixh p{font-size:13.5px;color:var(--sub)}
.ixb ul{list-style:none;margin:14px 0 0;padding:0}.ixb li a{display:flex;gap:10px;align-items:center;padding:7px 0;border-top:1px solid var(--line);font-size:15px}.ixb li a:hover{color:var(--ac)}.ixb li a>svg{width:17px;height:17px;color:var(--mute)}
.ixb li .n{font-family:"JetBrains Mono",monospace;color:var(--mute);font-size:12px;min-width:22px}.ixb li .c{margin-left:auto;color:var(--mute);font-size:13px;white-space:nowrap}
.chg{list-style:none;margin:12px 0 0;padding:0}.chg li{display:grid;grid-template-columns:96px 64px 1fr;gap:12px;padding:9px 0;border-top:1px solid var(--line);font-size:15px;align-items:center}.chg time{font-family:"JetBrains Mono",monospace;font-size:13px;color:var(--mute)}
.badge{font-size:12px;font-weight:700;color:var(--sub);border:1px solid var(--line2);border-radius:5px;padding:0 6px;justify-self:start;height:22px;line-height:20px}.badge.r{color:var(--ac);border-color:#C9D7F5;background:var(--ac-s)}
.covers{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:14px}.cv{display:block;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:#fff}.cv:hover{border-color:var(--ac)}.cv img{width:100%;aspect-ratio:16/9;object-fit:cover;background:#1D2330}
.cv div{padding:8px 10px 10px;display:flex;gap:8px;align-items:flex-start}.cv b{font-size:13.5px;line-height:1.4}.cv small{display:block;font-size:12px;color:var(--mute);font-weight:500}
.ft{border-top:1px solid var(--line);padding:24px 48px 40px;font-size:13px;color:var(--mute)}.ft b{color:var(--sub)}.ft p{margin-top:3px}.ft a{text-decoration:underline}
/* 챕터 */
.player{position:relative;aspect-ratio:16/9;border-radius:12px;overflow:hidden;background:#1D2330;margin-top:22px;border:1px solid var(--line);cursor:pointer}.player img{width:100%;height:100%;object-fit:cover}.player iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.player .play{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);display:flex;gap:10px;align-items:center;height:52px;padding:0 22px;border-radius:26px;background:#fff;color:var(--ink);font-weight:700;box-shadow:0 6px 20px rgba(0,0,0,.25);border:0;font-size:16px;cursor:pointer}.player .play svg{width:20px;height:20px;fill:currentColor}
.strip{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:8px;margin-top:10px}.strip a{position:relative;border-radius:6px;overflow:hidden;border:1px solid var(--line)}.strip a:hover{border-color:var(--ac)}.strip img{width:100%;aspect-ratio:16/9;object-fit:cover}
.strip span{position:absolute;left:4px;bottom:3px;font-size:11px;font-family:"JetBrains Mono",monospace;color:#fff;background:rgba(29,35,48,.75);border-radius:3px;padding:0 4px}
.tabsx{display:flex;gap:2px;border-bottom:1px solid var(--line);margin-top:28px;overflow-x:auto}.tabsx a{display:flex;gap:6px;align-items:center;padding:9px 14px;font-size:15px;color:var(--sub);white-space:nowrap}.tabsx a svg{width:16px;height:16px}.tabsx a[aria-current]{color:var(--ink);font-weight:700;box-shadow:inset 0 -2px 0 var(--ac)}
.btns{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}.btns a{display:flex;align-items:center;gap:7px;height:36px;padding:0 13px;border:1px solid var(--line2);border-radius:8px;font-size:14px;font-weight:600}.btns a:hover{border-color:var(--ac);color:var(--ac)}.btns svg{width:16px;height:16px}
.used{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px}.used a{display:flex;gap:10px;align-items:center;background:#fff;border:1px solid #C9D7F5;border-radius:10px;padding:8px 14px 8px 8px;font-weight:600;font-size:15px}.used a:hover{border-color:var(--ac)}
/* 사례 */
.libs{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-top:22px}.lb{display:flex;gap:10px;align-items:center;border:1px solid var(--line);border-radius:10px;padding:10px 12px}.lb:hover{border-color:var(--ac)}.lb[aria-current]{border-color:var(--ac);background:var(--ac-s)}
.lb b{display:block;font-size:14px;line-height:1.3}.lb small{color:var(--mute);font-size:12.5px}
.fl{display:flex;gap:8px;flex-wrap:wrap;margin-top:20px}.sel{display:flex;align-items:center;gap:6px;height:34px;padding:0 10px 0 12px;border:1px solid var(--line2);border-radius:8px;font-size:14px;color:var(--sub);background:#fff}.sel svg{width:15px;height:15px}
.diff{display:inline-flex;gap:2px}.diff i{width:7px;height:12px;border-radius:2px;background:var(--line2);display:block}.diff i.on{background:var(--ink)}
.run{display:inline-flex;gap:4px;align-items:center;font-size:12px;font-weight:700;color:#1F7A4D;background:#E8F4EE;border-radius:5px;padding:1px 7px;margin-left:6px;white-space:nowrap}.run svg{width:12px;height:12px}
${DLG_CSS({ scrim: "rgba(29,35,48,.4)", bg: "#fff", ink: "#1D2330", line: "#EAE9E6", sub: "#5F6675", r: "12px", hover: "#F4F3F0" })}
@media (max-width:1180px){.main{grid-template-columns:minmax(0,1fr);padding:32px 32px 72px}.otp{display:none}.tn a:not(.st){display:none}.hero{grid-template-columns:minmax(0,1fr)}.libs{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:860px){.top{grid-template-columns:auto minmax(0,1fr) auto}.side{display:none}.shell{grid-template-columns:1fr}.sf{margin-left:0}.sf kbd,.brand b{display:none}.mtg{display:grid;place-items:center;width:40px;height:40px;margin-left:8px;border:0;background:none}
.ix{grid-template-columns:1fr}.main{padding:24px 16px 64px}h1{font-size:28px}.ft{padding:24px 16px 40px}.pn{grid-template-columns:1fr}.pn .r{grid-column:1}.chg li{grid-template-columns:90px 1fr}.chg li .badge{display:none}.tn{padding:0 12px 0 8px}.brand{padding:0 0 0 12px}
.hide-m{display:none}.covers{grid-template-columns:repeat(2,minmax(0,1fr))}.strip{grid-template-columns:repeat(4,minmax(0,1fr))}.strip a:nth-child(n+5){display:none}.libs{grid-template-columns:1fr 1fr}.ict.lg{width:44px;height:44px}.th{gap:12px}}`;

const kit0 = kitFor();
const kit = { dlg: kit0.dlg, js: kit0.js + `<script>document.querySelectorAll('[data-player]').forEach(p=>p.onclick=()=>{if(p.querySelector('iframe'))return;p.innerHTML='<iframe src="'+p.dataset.player+'" title="슬라이드" allow="fullscreen"></iframe>'});</script>` };
const side = (on) => `<nav class="side" aria-label="전체 목차">
<h4>시작</h4><a href="home.html"${on === "home" ? ' class="on"' : ""}>${i("signpost")}처음 오셨나요</a><a href="home.html#start">${i("user")}나에게 맞는 시작점</a><a href="#">${i("book-a")}용어 사전</a>
<h4>로드맵 ${S.version}</h4>${S.stages.map((s) => `<a href="roadmap.html"${on === "roadmap" && s.no === 1 ? "" : ""}>${i(STAGE_IC[s.no])}${esc(stageShort(s.title))}<span class="c">${s.no}</span></a>${s.no === 2 && on === "topic" ? `<div class="sub">${s.areas.map((a, n) => `<a href="topic.html"${n === 0 ? ' class="on"' : ""}>${esc(a.t)}</a>`).join("")}</div>` : ""}`).join("")}
<h4>강의 · ${D.chapters.length}챕터</h4>${lecStages.map((s) => `<a href="chapter.html">${tile(s.logos[0], 18)}${esc(s.title)}<span class="c">${s.list.length}</span></a>${on === "chapter" && s.no === 4 ? `<div class="sub">${s.list.map((c) => `<a href="chapter.html"${c.no === "36" ? ' class="on"' : ""}><span class="n">${c.no}</span>${esc(short(c.title))}</a>`).join("")}</div>` : ""}`).join("")}
<a href="chapter.html">${i("lightbulb")}꿀팁 (번외)<span class="c">${D.extras.length}</span></a>
<h4>사례와 자료</h4>${LIB.map(([k, t, n]) => `<a href="cases.html"${on === "cases" && k === "cases" ? ' class="on"' : ""}>${i(LIB_IC[k])}${t}<span class="c">${n}</span></a>`).join("")}<a href="#">${i("milestone")}조직 성숙도</a>
<h4>그 밖</h4><a href="home.html#news">${i("megaphone")}소식</a><a href="#">${i("info")}이 사이트에 대해</a></nav>`;
const top = (cur) => `<header class="top"><a class="brand" href="home.html"><span class="mk">${i("book-open")}</span><b>${D.NAME}</b></a>
<button class="sf" data-search>${i("search")}<span>주제, 챕터, 명령어, 사례 찾기</span><kbd>/</kbd></button>
<nav class="tn" aria-label="메뉴">${MENU.map(([k, t, h]) => `<a href="${h}"${k === cur ? ' aria-current="page"' : ""}>${t}</a>`).join("")}<a class="st" href="home.html#start">시작하기</a><button class="mtg" aria-label="전체 목차">${i("menu")}</button></nav></header>`;
const foot = `<footer class="ft"><b>${FOOT}</b>${LIC.map((l) => `<p>${l}</p>`).join("")}<p>고칠 곳과 질문: <a href="mailto:${D.CONTACT}">${D.CONTACT}</a></p></footer>`;
const crumb = (xs) => `<nav class="crumb" aria-label="현재 위치">${xs.map(([t, h], n) => (h ? `<a href="${h}">${t}</a>` : `<span>${t}</span>`) + (n < xs.length - 1 ? i("chevron-right") : "")).join("")}</nav>`;
const lecs = (nos) => (nos.length ? `<span class="lec">${nos.map((n) => `<a href="chapter.html" title="${esc(byNo[n].title)}">${tile(byNo[n].logos[0], 18)}${n}</a>`).join("")}</span>` : `<span class="lec"><em>강의 준비 중</em></span>`);
const page = (title, cur, on, body, wide) => html(title, css, `${top(cur)}<div class="shell">${side(on)}<div><main class="main${wide ? " wide" : ""}">${body}</main>${foot}</div></div>`, kit);

/* 홈 그림: 로드맵 단계(왼쪽)와 이어진 강의 단계(오른쪽). 선은 roadmap-links 초안에서 계산해요 */
const lecStageOf = (n) => byNo[n].stage;
const pairs = [];
for (const s of S.stages) for (const ls of new Set(STAGE_LINKS[s.no].map(lecStageOf))) pairs.push([s.no, ls]);
const glyph = (k, x, y, sz) => { const L = LOGO[k]; return L.lucide ? `<svg x="${x}" y="${y}" width="${sz}" height="${sz}" viewBox="0 0 24 24" fill="none" stroke="${L.hex}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${IC[L.lucide]}</svg>` : `<svg x="${x}" y="${y}" width="${sz}" height="${sz}" viewBox="0 0 24 24" fill="${L.hex}"><path d="${L.path}"/></svg>`; };
const icg = (n, x, y) => `<svg x="${x}" y="${y}" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2459C9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${IC[n]}</svg>`;
const Y = (k) => 8 + k * 46;
const MAP = `<figure class="map"><svg viewBox="0 0 460 252" role="img" aria-label="로드맵 단계와 이어진 강의">
<g fill="none" stroke="#B4C7EE" stroke-width="1.5">${pairs.map(([a, b]) => `<path d="M178 ${Y(a - 1) + 18} C230 ${Y(a - 1) + 18} 230 ${Y(b - 1) + 18} 282 ${Y(b - 1) + 18}"/>`).join("")}</g>
${S.stages.map((s, k) => `<g><rect x="0.5" y="${Y(k) + 0.5}" width="178" height="35" rx="8" fill="#fff" stroke="#D9D7D2"/>${icg(STAGE_IC[s.no], 10, Y(k) + 10)}<text x="34" y="${Y(k) + 23}" font-size="14" font-weight="600" fill="#1D2330">${s.no}. ${esc(stageShort(s.title))}</text></g>`).join("")}
${lecStages.map((s, k) => `<g><rect x="282.5" y="${Y(k) + 0.5}" width="177" height="35" rx="8" fill="#fff" stroke="#D9D7D2"/>${s.logos.slice(0, 3).map((lg, j) => glyph(lg, 292 + j * 19, Y(k) + 10, 15)).join("")}<text x="${296 + Math.min(3, s.logos.length) * 19}" y="${Y(k) + 23}" font-size="13.5" font-weight="600" fill="#1D2330">${esc(s.title.replace("컨테이너와 데이터베이스", "컨테이너·DB"))}</text></g>`).join("")}
<text x="0" y="249" font-size="12" fill="#9298A4">로드맵 5단계</text><text x="460" y="249" font-size="12" fill="#9298A4" text-anchor="end">먼저 익힐 기초 강의</text></svg>
<figcaption>로드맵 주제를 열면 그 주제에 이어진 강의가 같이 나와요. 선은 이어진 곳이에요.</figcaption></figure>`;

/* 홈 */
const home = page(D.NAME, "", "home", `<div class="hero"><div><h1>AX 엔지니어 핸드북</h1><p class="desc">${esc(S.defn)}</p>
<button class="bigs" data-search>${i("search")}<span>무엇을 찾으세요? 예: 트랜잭션, MCP, 법인카드 정산</span><kbd>/</kbd></button>
<p class="hint">로드맵 주제, 강의 챕터, 명령어, 사례, 용어를 한 칸에서 찾아요. 어느 쪽에서든 <code>/</code>나 <code>Ctrl K</code>로 열려요.</p></div>${MAP}</div>
<div class="ix"><section class="ixb" id="start"><div class="ixh">${ict("signpost")}<div><h2>나에게 맞는 시작점</h2><p>경험에 가까운 줄에서 시작해요</p></div></div><ul>${[...S.start.map((r) => r.who), "지금 수업을 듣고 있다"].map((w, n) => `<li><a href="${n === 5 ? "chapter.html" : "roadmap.html"}">${i(START_IC[n])}${esc(w)}</a></li>`).join("")}</ul></section>
<section class="ixb"><div class="ixh">${ict("route")}<div><h2>로드맵 5단계</h2><p>원문 ax-engineer-roadmap ${S.version}</p></div></div><ul>${S.stages.map((s) => `<li><a href="roadmap.html">${i(STAGE_IC[s.no])}${esc(s.title)}<span class="c">${stageCount(s)}</span></a></li>`).join("")}</ul></section>
<section class="ixb"><div class="ixh">${ict("book-open")}<div><h2>기초 강의</h2><p>${D.chapters.length}챕터, 배우는 순서대로</p></div></div><ul>${lecStages.map((s) => `<li><a href="chapter.html">${logos(s.logos.slice(0, 3), 20)}${esc(s.title)}<span class="c">${s.from}–${s.to}</span></a></li>`).join("")}</ul></section>
<section class="ixb"><div class="ixh">${ict("layers")}<div><h2>사례와 자료</h2><p>옆에 펴 두고 보는 자료</p></div></div><ul>${LIB.map(([k, t, n]) => `<li><a href="cases.html">${i(LIB_IC[k])}${t}<span class="c">${n}</span></a></li>`).join("")}</ul></section></div>
<section style="margin-top:40px"><div class="ixh">${ict("presentation", "n")}<div><h2 style="font-size:18px">최근 올라온 강의</h2><p style="font-size:13.5px;color:var(--sub)">슬라이드 표지를 누르면 챕터로 가요</p></div></div>
<div class="covers">${["46", "45", "44", "43"].map((n) => `<a class="cv" href="chapter.html"><img src="${cover(n)}" alt="" loading="lazy"><div>${tile(byNo[n].logos[0], 22)}<b>${n} ${esc(short(byNo[n].title))}<small>${byNo[n].track} · ${byNo[n].level}</small></b></div></a>`).join("")}</div></section>
<section style="margin-top:40px" id="news"><div class="ixh">${ict("megaphone", "n")}<h2 style="font-size:18px">최근 바뀐 것</h2></div><ul class="chg">${NEWS.map(([d, k, t]) => `<li><time>${d}</time><span class="badge ${k === "로드맵" ? "r" : ""}">${k}</span><span>${t}</span></li>`).join("")}</ul></section>`, true);

/* 로드맵 */
const roadmap = page("로드맵 · " + D.NAME, "roadmap", "roadmap", `<div>${crumb([["홈", "home.html"], ["로드맵"]])}<div class="th">${ict("route", "lg")}<h1>AX 엔지니어 로드맵</h1></div><p class="desc">다섯 단계를 차례로 따라가요. 단계마다 읽을 문서, 다음 단계 전에 확인할 질문, 이어진 기초 강의가 있어요.</p>
<div class="metal"><span>${i("git-branch")}<span class="mono">ax-engineer-roadmap ${S.version}</span></span><span>${i("clock-3")}${S.commit.split("·")[1]} 기준</span><a href="${D.GH("README.md")}">${i("external-link")}원문 보기</a></div>
${S.stages.map((s) => `<section style="margin-top:44px"><div class="th">${ict(STAGE_IC[s.no])}<h2 id="st${s.no}">${s.no}. ${esc(s.title)}</h2></div><p style="color:var(--sub);margin-top:8px;max-width:780px">${esc(s.lede)}</p>
<div class="tbl"><table><thead><tr><th style="width:52px">#</th><th>주제</th><th class="hide-m">다루는 것</th><th>이어진 강의</th></tr></thead><tbody>${stageTopics(s).map((t, n) => { const id = s.areas?.[n]?.id; const d = s.docs?.[n]?.d ?? s.areas?.[n]?.q ?? s.projects?.[n]?.out ?? (s.no === 5 ? S.cases[n].area : "핵심 질문, 주요 작업, 산출물, 통과 기준"); return `<tr><td class="n">${s.no}.${n + 1}</td><td><span class="tt">${id ? ict(AREA_IC[id], "sm") : s.no === 5 ? ict(CASE_IC[S.cases[n].area] || "briefcase", "sm n") : ""}<a href="topic.html">${esc(t)}</a></span></td><td class="hide-m"><small>${esc(d)}</small></td><td>${id ? lecs(AREA_LINKS[id]) : s.no === 4 && n === 0 ? lecs(["09", "10", "44"]) : s.no === 3 && n === 3 ? lecs(["32", "45", "46"]) : `<span class="lec"><em>—</em></span>`}</td></tr>`; }).join("")}</tbody></table></div>
${s.checks.length ? `<div class="call">${ict("list-checks")}<div><h3>다음 단계로 가기 전에</h3>${s.checks.map((c) => `<p>${esc(c)}</p>`).join("")}</div></div>` : ""}</section>`).join("")}</div>
<aside class="otp"><h4>이 쪽의 내용</h4>${S.stages.map((s) => `<a href="#st${s.no}">${s.no}. ${esc(stageShort(s.title))}</a>`).join("")}</aside>`);

/* 로드맵 주제 */
const T = TOPIC;
const topic = page(T.title + " · 로드맵", "roadmap", "topic", `<article>${crumb([["로드맵", "roadmap.html"], ["2. " + stageShort(T.stage.title), "roadmap.html"], [T.title]])}<div class="th">${ict(AREA_IC[T.area.id], "lg")}<h1>${esc(T.title)}</h1></div><p class="desc">${esc(T.area.q)}</p>
<div class="metal"><span>${i("file-text")}<span class="mono">${T.src}</span></span><span>${i("git-branch")}${S.version}</span><a href="${D.GH(T.src)}">${i("pencil")}고치기 제안</a></div>
<section style="margin-top:28px"><div class="ixh">${ict("book-open")}<div><h3>먼저 익힐 기초 강의</h3><p style="font-size:14px;color:var(--sub)">이 문서를 읽기 전에 손에 익혀 두면 좋은 챕터 ${T.lec.length}개예요.</p></div></div>
<div class="covers">${T.lec.map((n) => `<a class="cv" href="chapter.html"><img src="${cover(n)}" alt="" loading="lazy"><div>${tile(byNo[n].logos[0], 22)}<b>${n} ${esc(short(byNo[n].title))}<small>${byNo[n].track} · ${byNo[n].level}</small></b></div></a>`).join("")}</div></section>
<div class="prose"><h2 id="why">왜 필요한가</h2><p>${esc(T.why)}</p><h2 id="know">알아야 할 것</h2></div>
<div class="tbl"><table><thead><tr><th>항목</th><th style="width:200px">이어진 강의</th></tr></thead><tbody>${T.know.map((k) => `<tr><td>${esc(k.t)}</td><td>${lecs(k.lec)}</td></tr>`).join("")}</tbody></table></div>
<div class="prose">${T.body.o}</div>
<p class="edit">${i("pencil")}이 문서는 로드맵 레포에서 고쳐요. <a href="${D.GH(T.src)}">GitHub에서 고치기 제안</a></p>
<div class="pn"><a class="r" href="topic.html"><span><small>다음</small><b>${esc(T.next.t)}</b></span>${ict(AREA_IC[T.next.id], "sm")}</a></div></article>
<aside class="otp"><h4>이 쪽의 내용</h4><a class="on" href="#why">왜 필요한가</a><a href="#know">알아야 할 것</a>${T.body.ids.map(([id, t]) => `<a href="#${id}">${esc(t)}</a>`).join("")}
<div class="blk"><h4>관련 자료</h4><a class="rel" href="cases.html">${i("briefcase")}${esc(S.cases[2].t)}</a><a class="rel" href="cases.html">${i("clipboard-check")}UI 통합 점검표</a></div></aside>`);

/* 강의 챕터 */
const c = CH.c;
const chapter = page(c.title + " · 강의", "lectures", "chapter", `<article>${crumb([["강의", "chapter.html"], [`${c.stage}. ${c.stageTitle}`, "chapter.html"], [`${c.no} ${short(c.title)}`]])}<div class="th">${logos(c.logos, 52)}<h1>${c.no}. ${esc(c.title)}</h1></div><p class="desc">${esc(c.goal.replace(/`/g, ""))}</p>
<div class="metal"><span>${i("layers")}${c.track} · ${c.level}</span><span>${i("presentation")}슬라이드 ${CH.slides.length}쪽</span><span>${i("file-text")}<span class="mono">${c.dir}/README.md</span></span></div>
<div class="player" data-player="${CH.deck}"><img src="${cover(c.no)}" alt="${esc(c.title)} 표지"><button class="play" type="button">${i("play")}슬라이드 보기</button></div>
<div class="strip" aria-label="슬라이드 미리보기">${Array.from({ length: 8 }, (_, k) => `<a href="#" title="${esc(CH.slides[k].t)}"><img src="../shared/slides36/${String(k + 1).padStart(2, "0")}.jpg" alt="" loading="lazy"><span>${k + 1}</span></a>`).join("")}</div>
<div class="btns"><a href="${CH.deck}">${i("presentation")}크게 보기</a><a href="${CH.pdf}">${i("download")}PDF 받기</a></div>
<nav class="tabsx" aria-label="챕터 안내"><a aria-current="page" href="#">${i("target")}개요</a><a href="#">${i("square-terminal")}명령어 요약</a><a href="#">${i("play")}실습</a><a href="#">${i("triangle-alert")}문제 해결</a></nav>
<div class="prose"><h2 id="g" style="border:0;margin-top:20px">배우는 것</h2><ul>${CH.goals.map((g) => `<li>${esc(g).replace(/`([^`]+)`/g, "<code>$1</code>")}</li>`).join("")}</ul><h2 id="p">구성</h2></div>
<div class="tbl"><table><thead><tr><th>파트</th><th class="r" style="width:96px">쪽</th></tr></thead><tbody>${CH.parts.map((p) => `<tr><td>${esc(p.p)}</td><td class="r"><small>${p.a}–${p.b}</small></td></tr>`).join("")}</tbody></table></div>
<div class="call">${ict("route")}<div><h3>이 챕터를 쓰는 로드맵 주제</h3><p>여기서 익힌 것을 로드맵의 이 주제에서 써요.</p><div class="used">${CH.used.map((u) => `<a href="topic.html">${ict("plug", "sm")}${esc(u)}</a>`).join("")}</div></div></div>
<div class="pn"><a href="chapter.html">${tile(CH.prev.logos[0], 28)}<span><small>이전</small><b>${CH.prev.no} ${esc(short(CH.prev.title))}</b></span></a><a class="r" href="chapter.html"><span><small>다음</small><b>${CH.next.no} ${esc(short(CH.next.title))}</b></span>${tile(CH.next.logos[0], 28)}</a></div></article>
<aside class="otp"><h4>슬라이드 파트</h4>${CH.parts.map((p, n) => `<a${n ? "" : ' class="on"'} href="#">${esc(p.p)}</a>`).join("")}<div class="blk"><h4>먼저 볼 챕터</h4><a class="rel" href="chapter.html">${tile(CH.prev.logos[0], 18)}${CH.prev.no} ${esc(short(CH.prev.title))}</a></div></aside>`);

/* 사례와 자료 */
const cases = page("사례와 자료 · " + D.NAME, "library", "cases", `<div>${crumb([["사례와 자료", "cases.html"], ["업무 사례"]])}<div class="th">${ict("briefcase", "lg")}<h1>업무 사례</h1></div><p class="desc">업무 하나를 원본 시스템, 승인 지점, 실패 대응까지 설계한 문서 ${S.cases.length}개예요. 실제 조직 성과가 아니라 공개 자료와 합성 데이터로 만든 설계예요.</p>
<nav class="libs" aria-label="사례와 자료">${LIB.map(([k, t, n]) => `<a class="lb" href="cases.html"${k === "cases" ? ' aria-current="page"' : ""}>${ict(LIB_IC[k], "sm")}<span><b>${t}</b><small>${n}${k === "jobs" ? "건" : "개"}</small></span></a>`).join("")}</nav>
<div class="fl"><span class="sel">분야: 전체 ${i("chevron-down")}</span><span class="sel">산업: 전체 ${i("chevron-down")}</span><span class="sel">난이도: 전체 ${i("chevron-down")}</span><span class="sel">근거: 전체 ${i("chevron-down")}</span><span class="sel" style="margin-left:auto">추천 순서 ${i("chevron-down")}</span></div>
<div class="tbl" style="overflow-x:auto"><table><thead><tr><th style="width:36px">#</th><th>사례</th><th class="hide-m">분야 · 산업</th><th>난이도</th><th class="hide-m">위험</th><th class="hide-m">프로젝트</th></tr></thead><tbody>
${S.cases.map((x, n) => `<tr><td class="n">${n + 1}</td><td><span class="tt">${ict(CASE_IC[x.area] || "briefcase", "sm n")}<span><a href="cases.html">${esc(x.t)}</a>${/재현 가능/.test(x.ev) ? `<span class="run">${i("play")}실행 예제</span>` : ""}</span></span></td><td class="hide-m"><small>${esc(x.area)} · ${esc(x.industry)}</small></td><td><span class="diff" title="난이도 ${x.diff}">${[1, 2, 3, 4, 5].map((k) => `<i class="${k <= x.diff ? "on" : ""}"></i>`).join("")}</span></td><td class="hide-m">${esc(x.risk)}</td><td class="hide-m mono" style="font-size:13px">${esc(x.p)}</td></tr>`).join("")}</tbody></table></div>
<p class="edit">${i("info")}초록 "실행 예제"는 직접 돌려 볼 수 있는 사례예요. 나머지는 실행 전 설계 문서예요.</p></div>`, true);

for (const [f, h] of Object.entries({ home, roadmap, topic, chapter, cases })) write("v15", f + ".html", h);
console.log("v15 ok");
