// 시안 v11 · 노선도. 로드맵은 굵은 한 줄, 강의는 분류 색의 줄로 그려요. 지금 위치와 다음 걸음이 늘 줄 위에 보여요.
import * as D from "../plan/data.mjs";
const { i, esc, S, byNo, short, stageShort, TOPIC, CH, LIB, NEWS, MENU, FOOT, LIC, html, DLG_CSS, kitFor, AREAS, stageTopics, stageCount, STAGE_LINKS, AREA_LINKS, SOON, HIRE_TOTAL, lecStages } = D;
import { write } from "../lib.mjs";

const TC = { 터미널: "#3F4757", Git: "#A0620A", GitHub: "#5A3BB8", 파이썬: "#1E5FA8", Docker: "#0F7C86", 데이터베이스: "#A23B72" };
const LSC = ["#A0620A", "#1E5FA8", "#0F7C86", "#A23B72", "#3F4757"];
const css = `:root{--bg:#FAFAF8;--card:#fff;--ink:#1D2330;--sub:#5D6474;--mute:#8C92A0;--line:#E4E2DC;--rail:#1D2330;--ac:#2459C9;--ac-s:#EAF0FC}
body{background:var(--bg);color:var(--ink);font-size:16px;line-height:1.6}.w{max-width:1200px;margin:0 auto;padding:0 32px}
.hd{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}.hd .w{display:flex;align-items:center;gap:28px;height:64px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:17px}.mk{width:28px;height:28px;position:relative}.mk::before{content:"";position:absolute;left:2px;right:2px;top:12px;height:4px;background:var(--rail);border-radius:2px}
.mk::after{content:"";position:absolute;left:8px;top:7px;width:14px;height:14px;border-radius:50%;background:#fff;box-shadow:inset 0 0 0 4px var(--ac)}
.nav{display:flex;gap:4px}.nav a{padding:8px 12px;border-radius:8px;font-weight:600;color:var(--sub)}.nav a:hover{color:var(--ink);background:#F1F0EC}.nav a[aria-current]{color:var(--ink);box-shadow:inset 0 -3px 0 var(--ac);border-radius:0}
.hr{margin-left:auto;display:flex;gap:8px;align-items:center}.st{height:38px;padding:0 16px;border-radius:19px;background:var(--ink);color:#fff;font-weight:700;display:flex;align-items:center;gap:6px;font-size:15px}
.sb{height:38px;width:38px;border-radius:19px;border:1px solid var(--line);background:var(--card);display:grid;place-items:center;cursor:pointer}
h1{font-size:46px;line-height:1.2;font-weight:800;letter-spacing:-.025em}h2{font-size:28px;line-height:1.3;font-weight:800;letter-spacing:-.015em}h3{font-size:18px;font-weight:700;line-height:1.4}
.eyebrow{display:inline-flex;gap:8px;align-items:center;font-size:14px;font-weight:700;color:var(--sub)}.eyebrow i{width:10px;height:10px;border-radius:50%;box-shadow:inset 0 0 0 3px var(--ac);display:block}
main{padding:40px 0 80px}.sec{margin-top:72px}.sh{display:flex;justify-content:space-between;align-items:end;gap:16px;margin-bottom:20px}.sh p{color:var(--sub);margin-top:4px}.more{display:flex;gap:6px;align-items:center;font-weight:600;color:var(--ac);white-space:nowrap}
/* 큰 노선 */
.line{position:relative;display:grid;grid-template-columns:repeat(5,1fr);margin-top:36px}.line::before{content:"";position:absolute;left:10%;right:10%;top:21px;height:8px;border-radius:4px;background:var(--rail)}
.stn{position:relative;text-align:center;padding:0 10px;color:inherit}.stn .o{width:50px;height:50px;border-radius:50%;margin:0 auto;background:#fff;box-shadow:inset 0 0 0 7px var(--rail);display:grid;place-items:center;font-weight:800;font-size:18px}
.stn.on .o{box-shadow:inset 0 0 0 7px var(--ac);color:var(--ac)}.stn h3{margin-top:12px;font-size:17px}.stn small{display:block;color:var(--sub);font-size:14px}.stn:hover h3{color:var(--ac)}
.xf{display:flex;gap:4px;justify-content:center;margin-top:8px}.xf i{width:10px;height:10px;border-radius:50%;display:block}
.lrail{margin-top:34px;display:grid;grid-template-columns:repeat(5,1fr);gap:6px}.lrail a{display:block;padding:12px 0 0;border-top:6px solid;font-size:14px;color:var(--sub)}.lrail b{display:block;color:var(--ink);font-size:15px}
.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:13px;color:var(--sub);margin-top:14px}.legend span{display:flex;gap:6px;align-items:center}.legend i{width:18px;height:5px;border-radius:3px;display:block}
.hero{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:56px;align-items:end}.hero p{font-size:18px;color:var(--sub);margin-top:16px;max-width:560px}
.hero .note{border-left:3px solid var(--line);padding-left:16px;font-size:15px;color:var(--sub)}
/* 출발점 */
.dep{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.dep a{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;display:flex;flex-direction:column;gap:10px}.dep a:hover{border-color:var(--ink)}
.dep b{font-size:16px}.mini{display:flex;align-items:center;gap:0;margin-top:auto;font-size:13px;color:var(--sub)}.mini i{width:12px;height:12px;border-radius:50%;box-shadow:inset 0 0 0 3px var(--rail);flex:none;display:block;background:#fff}
.mini s{flex:1;height:3px;background:var(--rail);min-width:16px;text-decoration:none}.mini em{font-style:normal;margin-left:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.mini i.ac{box-shadow:inset 0 0 0 3px var(--ac)}
.panel{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px 24px}
.two{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px}
.bars{margin-top:14px}.bar{display:grid;grid-template-columns:80px 1fr 40px;gap:10px;align-items:center;font-size:14px;margin:8px 0}.bar i{height:8px;border-radius:4px;background:var(--rail);display:block}.bar em{font-style:normal;text-align:right;font-variant-numeric:tabular-nums}
.big{font-size:44px;font-weight:800;letter-spacing:-.02em;line-height:1;margin-top:10px}.big small{font-size:18px;margin-left:4px}
.news{list-style:none;margin:0;padding:0}.news li{display:flex;gap:14px;padding:12px 0;border-bottom:1px solid var(--line);align-items:baseline}.news li:last-child{border:0}.news time{font-size:14px;color:var(--sub);width:92px;flex:none;font-variant-numeric:tabular-nums}
.k{font-size:12px;font-weight:700;padding:1px 8px;border-radius:10px;flex:none}.k.r{background:var(--ink);color:#fff}.k.l{background:#fff;box-shadow:inset 0 0 0 1.5px var(--ink)}
.ft{border-top:1px solid var(--line);padding:32px 0 48px;color:var(--sub);font-size:14px}.ft b{color:var(--ink)}.ft p{margin-top:4px}.ft a{text-decoration:underline}
/* 세로 노선 */
.vline{position:relative;margin-top:40px}.vs{position:relative;display:grid;grid-template-columns:72px minmax(0,1fr);gap:0 20px;padding-bottom:44px}
.vs::before{content:"";position:absolute;left:32px;top:30px;bottom:-4px;width:8px;background:var(--rail);border-radius:4px}.vs:last-child::before{display:none}
.vs .o{width:72px;height:72px;border-radius:50%;background:var(--bg);box-shadow:inset 0 0 0 8px var(--rail);display:grid;place-items:center;font-size:24px;font-weight:800;position:relative;z-index:1}
.vs h2{font-size:26px;padding-top:14px}.vs .lede{color:var(--sub);margin-top:6px;max-width:760px}
.topics{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px;margin-top:18px}
.tp{position:relative;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px 14px 40px}.tp:hover{border-color:var(--ink)}
.tp::before{content:"";position:absolute;left:14px;top:18px;width:14px;height:14px;border-radius:50%;box-shadow:inset 0 0 0 3.5px var(--rail);background:#fff}
.tp b{display:block;font-size:15px}.tp small{display:flex;gap:4px;align-items:center;color:var(--sub);font-size:13px;margin-top:6px;flex-wrap:wrap}.tp small i{width:9px;height:9px;border-radius:50%;display:block}
.tp.soon small{color:var(--mute)}.chk{margin-top:14px;font-size:14px;color:var(--sub);display:flex;flex-direction:column;gap:4px}.chk span{display:flex;gap:8px}.chk svg{width:16px;height:16px;margin-top:3px;color:var(--ac)}
/* 지금 위치 */
.here{background:var(--card);border-bottom:1px solid var(--line)}.here .w{padding-top:18px;padding-bottom:18px}.here small{font-size:13px;color:var(--sub);font-weight:700}
.hl{display:flex;align-items:flex-start;margin-top:12px;overflow-x:auto;padding-bottom:4px}.hl a{flex:1;min-width:96px;text-align:center;position:relative;font-size:13px;color:var(--sub);padding-top:26px}
.hl a::before{content:"";position:absolute;top:6px;left:0;right:0;height:5px;background:var(--rail)}.hl a:first-child::before{left:50%}.hl a:last-child::before{right:50%}
.hl a::after{content:"";position:absolute;top:0;left:50%;margin-left:-8px;width:16px;height:16px;border-radius:50%;background:#fff;box-shadow:inset 0 0 0 4px var(--rail)}
.hl a.on{color:var(--ink);font-weight:700}.hl a.on::after{width:22px;height:22px;margin-left:-11px;top:-3px;box-shadow:inset 0 0 0 6px var(--ac)}
.hl.lc a::before{background:var(--c)}.hl.lc a::after{box-shadow:inset 0 0 0 4px var(--c)}.hl.lc a.on::after{box-shadow:inset 0 0 0 6px var(--c);background:var(--c)}
.page{display:grid;grid-template-columns:minmax(0,1fr) 280px;gap:56px;margin-top:36px}.q{font-size:20px;color:var(--sub);margin-top:12px}
.xfer{margin-top:28px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px 22px}.xfer h3{display:flex;gap:8px;align-items:center}.xfer p{color:var(--sub);font-size:14px;margin-top:2px}
.lst{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}.lst a{display:flex;align-items:center;gap:8px;padding:6px 12px 6px 6px;border-radius:20px;background:var(--bg);border:1px solid var(--line);font-size:14px}.lst a:hover{border-color:var(--ink)}
.lst a b{width:28px;height:28px;border-radius:50%;display:grid;place-items:center;color:#fff;font-size:12px;font-variant-numeric:tabular-nums}
.know{list-style:none;padding:0;margin:16px 0 0}.know li{display:grid;grid-template-columns:20px minmax(0,1fr) auto;gap:12px;padding:12px 0;border-bottom:1px solid var(--line);align-items:baseline}
.know li::before{content:"";width:12px;height:12px;border-radius:50%;box-shadow:inset 0 0 0 3px var(--rail);background:#fff;margin-top:5px}.know .c{display:flex;gap:4px;flex-wrap:wrap;justify-content:flex-end}
.know .c a{font-size:12px;font-weight:700;color:#fff;padding:2px 8px;border-radius:10px}.know .c em{font-style:normal;font-size:13px;color:var(--mute)}
.prose{max-width:760px}.prose h2{margin:48px 0 12px;font-size:24px}.prose h3{margin:26px 0 8px}.prose p{margin:12px 0}.prose ul,.prose ol{padding-left:22px}.prose li{margin:5px 0}.prose a{color:var(--ac);text-decoration:underline}
code{font-size:.88em;background:#F1F0EC;padding:1px 5px;border-radius:4px}.tw{overflow-x:auto;margin:16px 0;background:var(--card);border:1px solid var(--line);border-radius:12px}table{border-collapse:collapse;width:100%;font-size:15px}
.tw th,.tw td{text-align:left;vertical-align:top;padding:10px 14px;border-bottom:1px solid var(--line)}.tw tr:last-child td{border:0}.tw th{background:#F6F5F1}
.toc{position:sticky;top:88px}.toc h3{font-size:14px;color:var(--sub)}.toc ol{list-style:none;padding:0;margin:10px 0 0;border-left:2px solid var(--line)}.toc li a{display:block;padding:5px 0 5px 14px;font-size:14px;color:var(--sub);margin-left:-2px;border-left:2px solid transparent}
.toc li a:hover{color:var(--ink);border-color:var(--ink)}.toc .box{margin-top:28px;padding-top:18px;border-top:1px solid var(--line);font-size:14px}.toc .box a{color:var(--ac);display:block;margin-top:6px}
.nexts{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:56px}.nexts a{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 20px}.nexts a:hover{border-color:var(--ink)}.nexts small{color:var(--sub);display:flex;gap:6px;align-items:center}.nexts b{font-size:17px}.nexts .r{text-align:right}.nexts .r small{justify-content:flex-end}
.deck{position:relative;aspect-ratio:16/9;border-radius:14px;overflow:hidden;background:#111;margin-top:28px}.deck iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.acts{display:flex;gap:10px;margin-top:14px;flex-wrap:wrap}.acts a{display:flex;align-items:center;gap:8px;height:40px;padding:0 16px;border-radius:20px;border:1px solid var(--line);background:var(--card);font-weight:600;font-size:15px}.acts a.p{background:var(--ink);color:#fff;border-color:var(--ink)}
.goals{list-style:none;padding:0;margin:12px 0 0}.goals li{display:flex;gap:10px;padding:8px 0;border-bottom:1px solid var(--line)}.goals svg{width:18px;height:18px;margin-top:3px;color:var(--c)}
/* 사례 */
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:22px}.chips button{height:36px;padding:0 14px;border-radius:18px;border:1px solid var(--line);background:var(--card);font-size:14px;cursor:pointer}.chips button[aria-pressed=true]{background:var(--ink);color:#fff;border-color:var(--ink)}
.lib{display:flex;gap:6px;margin-top:24px;border-bottom:1px solid var(--line);overflow-x:auto}.lib a{padding:10px 14px;font-weight:600;color:var(--sub);white-space:nowrap}.lib a[aria-current]{color:var(--ink);box-shadow:inset 0 -3px 0 var(--ink)}.lib a em{font-style:normal;color:var(--mute);margin-left:4px;font-weight:500}
.cg{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:22px}.cc{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;display:flex;flex-direction:column;gap:10px}.cc:hover{border-color:var(--ink)}
.cc small{color:var(--sub);font-size:13px}.cc b{font-size:16px;line-height:1.45}.pr{display:flex;align-items:center;margin-top:auto;padding-top:6px}.pr span{display:flex;flex-direction:column;align-items:center;gap:4px;font-size:11px;color:var(--mute);flex:none;width:22px}
.pr span i{width:14px;height:14px;border-radius:50%;box-shadow:inset 0 0 0 3px #D3D1CA;background:#fff;display:block}.pr span.on i{box-shadow:inset 0 0 0 4px var(--rail)}.pr span.on{color:var(--ink);font-weight:700}.pr s{flex:1;height:3px;background:#D3D1CA;margin-bottom:17px;text-decoration:none}.pr s.on{background:var(--rail)}
.cg.lb5{grid-template-columns:repeat(5,1fr)}.meta{display:flex;gap:6px;flex-wrap:wrap}.meta span{font-size:12px;padding:2px 8px;border-radius:10px;background:#F1F0EC;color:var(--sub)}
${DLG_CSS({ scrim: "rgba(29,35,48,.45)", bg: "#fff", ink: "#1D2330", line: "#E4E2DC", sub: "#5D6474", r: "14px", hover: "#F1F0EC" })}
@media (max-width:1000px){.dep,.cg{grid-template-columns:1fr 1fr}.cg.lb5{grid-template-columns:repeat(3,1fr)}.hero{grid-template-columns:1fr;gap:24px}.page{grid-template-columns:1fr}.toc{display:none}.nav{display:none}}
@media (max-width:680px){.cg.lb5{grid-template-columns:1fr 1fr}.w{padding:0 16px}h1{font-size:32px}h2{font-size:23px}.dep,.cg,.two,.nexts{grid-template-columns:1fr}.st span{display:none}.st{padding:0 12px}
.line{grid-template-columns:1fr;gap:18px}.line::before{left:21px;right:auto;top:20px;bottom:20px;width:8px;height:auto}.stn{display:grid;grid-template-columns:50px 1fr;gap:4px 14px;text-align:left;padding:0}.stn .o{grid-row:1/4;margin:0}.stn h3{margin-top:2px}.xf{justify-content:flex-start;margin-top:2px}
.lrail{grid-template-columns:1fr 1fr}.vs{grid-template-columns:52px minmax(0,1fr);gap:0 14px}.vs .o{width:52px;height:52px;font-size:19px;box-shadow:inset 0 0 0 6px var(--rail)}.vs::before{left:22px}.vs h2{font-size:21px;padding-top:10px}
.know li{grid-template-columns:20px minmax(0,1fr)}.know .c{grid-column:2;justify-content:flex-start}}`;

const kit = kitFor();
const head = (cur) => `<header class="hd"><div class="w"><a class="brand" href="home.html"><span class="mk"></span>${D.NAME}</a>
<nav class="nav" aria-label="메뉴">${MENU.map(([k, t, h]) => `<a href="${h}"${k === cur ? ' aria-current="page"' : ""}>${t}</a>`).join("")}</nav>
<div class="hr"><a class="st" href="home.html#start">${i("signpost")}<span>시작하기</span></a><button class="sb" data-search aria-label="찾기">${i("search")}</button></div></div></header>`;
const foot = `<footer class="ft"><div class="w"><b>${FOOT}</b>${LIC.map((l) => `<p>${l}</p>`).join("")}<p>고칠 곳과 질문: <a href="mailto:${D.CONTACT}">${D.CONTACT}</a></p></div></footer>`;
const lecDots = (nos) => nos.map((n) => `<i style="background:${TC[byNo[n].track]}" title="${n} ${esc(byNo[n].title)}"></i>`).join("");
const stLec = (s) => [...new Set(STAGE_LINKS[s.no])];

/* 홈 */
const home = html(D.NAME, css, `${head("")}<main><div class="w">
<section class="hero"><div><span class="eyebrow"><i></i>AX 엔지니어 공개 로드맵 ${S.version}</span><h1 style="margin-top:14px">어디서 출발하든<br> 같은 노선 위에서 만나요</h1><p>${esc(S.defn)}</p></div>
<p class="note">굵은 검은 줄이 로드맵 5단계예요. 아래 색 줄은 기초 강의 ${D.chapters.length}챕터이고, 점은 그 단계에 이어진 강의예요.</p></section>
<div class="line" aria-label="로드맵 5단계">${S.stages.map((s) => `<a class="stn${s.no === 1 ? " on" : ""}" href="roadmap.html"><span class="o">${s.no}</span><h3>${esc(stageShort(s.title))}</h3><small>${stageCount(s)}</small><span class="xf">${lecDots(stLec(s).slice(0, 8))}</span></a>`).join("")}</div>
<div class="lrail" aria-label="기초 강의">${lecStages.map((s, n) => `<a href="chapter.html" style="border-color:${LSC[n]}"><b>${esc(s.title)}</b>${s.from}–${s.to}</a>`).join("")}</div>
<div class="legend">${Object.entries(TC).map(([k, v]) => `<span><i style="background:${v}"></i>${k}</span>`).join("")}</div>
<section class="sec" id="start"><div class="sh"><div><h2>출발점 고르기</h2><p>지금 내 경험에 가까운 곳에서 타요. 모두 4단계의 첫 프로젝트 P1에서 만나요.</p></div></div>
<div class="dep">${S.start.map((r) => `<a href="roadmap.html"><b>${esc(r.who)}</b><span style="color:var(--sub);font-size:14px">첫 결과물 · ${esc(r.first)}</span><span class="mini"><i class="ac"></i><s></s><i></i><s></s><i></i><em>${esc(r.go.split("→")[0].trim())}</em></span></a>`).join("")}
<a href="chapter.html"><b>지금 수업을 듣고 있다</b><span style="color:var(--sub);font-size:14px">오늘 배운 챕터의 슬라이드와 PDF를 다시 봐요</span><span class="mini"><i class="ac"></i><s style="background:#A23B72"></s><i></i><em>강의 챕터로</em></span></a></div></section>
<section class="sec two"><div class="panel"><div class="sh" style="margin:0"><h3>이번 달 채용 공고</h3><a class="more" href="cases.html">공고 보기 ${i("arrow-right")}</a></div><div class="big">${HIRE_TOTAL}<small>건</small></div><p style="color:var(--sub);font-size:14px;margin-top:6px">2026년 10월, 국내 AX·AI Agent·FDE</p>
<div class="bars">${S.hiring.rows.map((r) => `<div class="bar"><span>${r.type}</span><i style="width:${Math.round((r.n / 72) * 100)}%"></i><em>${r.n}</em></div>`).join("")}</div><p style="font-size:13px;color:var(--mute);margin-top:8px">${esc(S.hiring.note)}</p></div>
<div class="panel" id="news"><div class="sh" style="margin:0 0 6px"><h3>소식</h3><a class="more" href="#">전체 ${i("arrow-right")}</a></div><ul class="news">${NEWS.map(([d, k, t]) => `<li><time>${d}</time><span class="k ${k === "강의" ? "l" : "r"}">${k}</span><span>${t}</span></li>`).join("")}</ul></div></section>
<section class="sec"><div class="sh"><div><h2>사례와 자료</h2><p>노선을 따라가며 옆에 펴 두는 자료예요.</p></div><a class="more" href="cases.html">모두 보기 ${i("arrow-right")}</a></div>
<div class="cg" style="grid-template-columns:repeat(5,1fr);margin-top:0">${LIB.map((l) => `<a class="cc" href="cases.html"><small>${l[1]}</small><span class="big" style="font-size:34px;margin:0">${l[2]}</span><small>${l[3]}</small></a>`).join("")}</div></section>
</div></main>${foot}`, kit).replace('class="cg" style="grid-template-columns:repeat(5,1fr);margin-top:0"', 'class="cg lb5" style="margin-top:0"');

/* 로드맵 */
const roadmap = html("로드맵 · " + D.NAME, css, `${head("roadmap")}<main><div class="w">
<span class="eyebrow"><i></i>로드맵 ${S.version} · 원문 ax-engineer-roadmap</span><h1 style="margin-top:12px">AX 엔지니어 로드맵</h1><p class="q">한 역에서 점검 질문에 답할 수 있으면 다음 역으로 가요. 작은 점은 그 주제에 이어진 기초 강의예요.</p>
<div class="vline">${S.stages.map((s) => `<section class="vs"><span class="o">${s.no}</span><div><h2>${esc(s.title)}</h2><p class="lede">${esc(s.lede)}</p>
<div class="topics">${stageTopics(s).map((t, n) => { const id = s.areas?.[n]?.id; const ls = id ? AREA_LINKS[id] : []; return `<a class="tp${id && SOON[id] ? " soon" : ""}" href="topic.html"><b>${esc(t)}</b>${id ? `<small>${lecDots(ls)}${ls.length ? ` 강의 ${ls.length}` : ""}${SOON[id] ? ` · 준비 중: ${SOON[id]}` : ""}</small>` : ""}</a>`; }).join("")}</div>
${s.checks.length ? `<div class="chk">${s.checks.map((c) => `<span>${i("circle-check")}${esc(c)}</span>`).join("")}</div>` : ""}</div></section>`).join("")}</div>
</div></main>${foot}`, kit);

/* 로드맵 주제 */
const T = TOPIC;
const topic = html(T.title + " · 로드맵", css, `${head("roadmap")}<div class="here"><div class="w"><small>2단계 ${esc(stageShort(T.stage.title))} · 7영역</small>
<div class="hl">${T.stage.areas.map((a, n) => `<a href="topic.html"${n === 0 ? ' class="on" aria-current="page"' : ""}>${esc(a.t)}</a>`).join("")}</div></div></div>
<main style="padding-top:0"><div class="w"><div class="page"><article><h1>${esc(T.title)}</h1><p class="q">${esc(T.area.q)}</p>
<div class="xfer"><h3>${i("book-open")}먼저 익힐 기초 강의</h3><p>이 주제를 읽기 전에 손에 익혀 둘 챕터예요. 색은 강의 분류예요.</p>
<div class="lst">${T.lec.map((n) => `<a href="chapter.html"><b style="background:${TC[byNo[n].track]}">${n}</b>${esc(short(byNo[n].title))}</a>`).join("")}</div></div>
<div class="prose"><h2>왜 필요한가</h2><p>${esc(T.why)}</p><h2>알아야 할 것</h2></div>
<ul class="know">${T.know.map((k) => `<li><span>${esc(k.t)}</span><span class="c">${k.lec.length ? k.lec.map((n) => `<a href="chapter.html" style="background:${TC[byNo[n].track]}">${n}</a>`).join("") : "<em>강의 준비 중</em>"}</span></li>`).join("")}</ul>
<div class="prose">${T.body.o}</div>
<div class="nexts"><a href="roadmap.html"><small>${i("arrow-left")}2단계 처음으로</small><b>${esc(T.stage.title)}</b></a><a class="r" href="topic.html"><small>다음 역 ${i("arrow-right")}</small><b>${esc(T.next.t)}</b></a></div></article>
<aside class="toc"><h3>이 쪽의 내용</h3><ol><li><a href="#">왜 필요한가</a></li><li><a href="#">알아야 할 것</a></li>${T.body.ids.map(([id, t]) => `<li><a href="#${id}">${esc(t)}</a></li>`).join("")}</ol>
<div class="box"><b>관련 자료</b><a href="cases.html">${esc(S.cases[2].t)}</a><a href="cases.html">UI 통합 점검표</a></div><div class="box"><b>원문</b><a href="${D.GH(T.src)}">${T.src.split("/").pop()} · ${S.version}</a></div></aside></div>
</div></main>${foot}`, kit);

/* 강의 챕터 */
const c = CH.c, ls = lecStages[c.stage - 1], col = LSC[c.stage - 1];
const chapter = html(c.title + " · 강의", css, `${head("lectures")}<div class="here"><div class="w"><small>강의 ${c.stage}단계 ${esc(c.stageTitle)} · ${ls.from}–${ls.to}</small>
<div class="hl lc" style="--c:${col}">${ls.list.map((x) => `<a href="chapter.html"${x.no === c.no ? ' class="on" aria-current="page"' : ""}>${x.no}</a>`).join("")}</div></div></div>
<main style="padding-top:0"><div class="w" style="--c:${col}"><div class="page"><article><span class="eyebrow" style="margin-top:36px;display:flex"><i style="box-shadow:inset 0 0 0 3px ${col}"></i>${c.track} · ${c.level}</span><h1 style="margin-top:10px">${esc(c.title)}</h1><p class="q">${esc(c.goal.replace(/`/g, ""))}</p>
<div class="deck"><iframe src="${CH.deck}" title="${esc(c.title)} 슬라이드" loading="lazy"></iframe></div>
<div class="acts"><a class="p" href="${CH.deck}">${i("presentation")}크게 보기</a><a href="${CH.pdf}">${i("download")}PDF 받기</a></div>
<div class="prose"><h2>이 챕터를 마치면</h2></div><ul class="goals">${CH.goals.map((g) => `<li>${i("circle-check")}<span>${esc(g).replace(/`([^`]+)`/g, "<code>$1</code>")}</span></li>`).join("")}</ul>
<div class="xfer" style="margin-top:36px"><h3>${i("route")}이 챕터를 쓰는 로드맵 주제</h3><p>여기서 익힌 것을 로드맵에서 어디에 쓰는지 보여 줘요.</p><div class="lst">${CH.used.map((u) => `<a href="topic.html"><b style="background:var(--rail)">2</b>${esc(u)}</a>`).join("")}</div></div>
<div class="nexts"><a href="chapter.html"><small>${i("arrow-left")}이전 역</small><b>${CH.prev.no} ${esc(short(CH.prev.title))}</b></a><a class="r" href="chapter.html"><small>다음 역 ${i("arrow-right")}</small><b>${CH.next.no} ${esc(short(CH.next.title))}</b></a></div></article>
<aside class="toc" style="margin-top:36px"><h3>구성</h3><ol>${CH.parts.map((p) => `<li><a href="#">${esc(p.p)} <span style="color:var(--mute)">${p.a}–${p.b}</span></a></li>`).join("")}</ol></aside></div>
</div></main>${foot}`, kit);

/* 사례와 자료 */
const pset = (p) => { const m = /P(\d)~P(\d)/.exec(p); if (m) return new Set(Array.from({ length: m[2] - m[1] + 1 }, (_, k) => +m[1] + k)); return new Set([...p.matchAll(/P(\d)/g)].map((x) => +x[1])); };
const route = (p) => { const s = pset(p); return `<span class="pr" title="프로젝트 ${esc(p)}">${[1, 2, 3, 4, 5].map((n) => `${n > 1 ? `<s class="${s.has(n) && s.has(n - 1) ? "on" : ""}"></s>` : ""}<span class="${s.has(n) ? "on" : ""}"><i></i>P${n}</span>`).join("")}</span>`; };
const cases = html("사례와 자료 · " + D.NAME, css, `${head("library")}<main><div class="w">
<span class="eyebrow"><i></i>사례와 자료</span><h1 style="margin-top:12px">업무 사례</h1><p class="q">업무 하나를 원본 시스템, 승인 지점, 실패 대응까지 설계한 문서예요. 카드 아래 줄은 그 사례로 연습하는 프로젝트 단계예요.</p>
<nav class="lib" aria-label="사례와 자료">${LIB.map(([k, t, n]) => `<a href="cases.html"${k === "cases" ? ' aria-current="page"' : ""}>${t}<em>${n}</em></a>`).join("")}</nav>
<div class="chips"><button aria-pressed="true">전체 ${S.cases.length}</button>${AREAS.map((a) => `<button aria-pressed="false">${esc(a)} ${S.cases.filter((x) => x.area === a).length}</button>`).join("")}</div>
<div class="cg">${S.cases.map((x) => `<a class="cc" href="cases.html"><small>${esc(x.area)} · ${esc(x.industry)}</small><b>${esc(x.t)}</b><span class="meta"><span>난이도 ${x.diff}</span><span>위험 ${esc(x.risk)}</span><span>${esc(x.ev)}</span></span>${route(x.p)}</a>`).join("")}</div>
<p style="margin-top:20px;font-size:14px;color:var(--sub)">업무 사례는 실제 조직의 성과가 아니에요. 공개 자료와 합성 데이터로 만든 설계예요.</p>
</div></main>${foot}`, kit);

for (const [f, h] of Object.entries({ home, roadmap, topic, chapter, cases })) write("v11", f + ".html", h);
console.log("v11 ok");
