// 시안 v10 · 안내서. 공공 기관 안내 페이지처럼 글과 순서가 앞에 서요. 카드 대신 줄과 번호로 나눠요.
import * as D from "../plan/data.mjs";
const { i, esc, S, byNo, short, stageShort, TOPIC, CH, LIB, NEWS, MENU, FOOT, LIC, html, DLG_CSS, kitFor, AREAS, stageTopics, stageCount, STAGE_LINKS, AREA_LINKS, SOON, HIRE_TOTAL } = D;
import { write } from "../lib.mjs";

const css = `:root{--bg:#fff;--ink:#0B0C0C;--sub:#505A5F;--line:#B1B4B6;--line2:#E3E4E5;--ac:#2459C9;--ac-d:#1A3F8F;--soft:#F3F2F1;--ok:#1F7A4D;--focus:#FFD43B}
body{background:var(--bg);color:var(--ink);font-size:17px;line-height:1.6}
.w{max-width:1040px;margin:0 auto;padding:0 24px}
a.l,.prose a,.lk a{color:var(--ac);text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px}a.l:hover,.prose a:hover{color:var(--ac-d);text-decoration-thickness:2px}
.top{background:var(--ink);color:#fff}.top .w{display:flex;align-items:center;gap:24px;height:60px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:18px;letter-spacing:-.01em}.brand svg{width:22px;height:22px}
.nav{display:flex;gap:2px;margin-left:auto}.nav a{padding:8px 12px;font-weight:600;font-size:16px;border-bottom:4px solid transparent;margin-bottom:-4px}.nav a[aria-current]{border-color:#fff}
.nav a:hover{text-decoration:underline}.stl{font-weight:700;font-size:15px;background:#fff;color:var(--ink);height:36px;padding:0 14px;display:flex;align-items:center}.stl:hover{background:var(--focus)}.sbtn{display:flex;align-items:center;gap:8px;height:36px;padding:0 12px;border:1px solid #fff;background:none;color:#fff;cursor:pointer;font-size:15px}
.bar{border-bottom:1px solid var(--line2)}.bar .w{display:flex;gap:10px;align-items:center;min-height:44px;font-size:15px;color:var(--sub)}
.tag{display:inline-block;white-space:nowrap;font-size:13px;font-weight:700;letter-spacing:.02em;padding:2px 8px;background:var(--ac);color:#fff}.tag.lc{background:var(--ok)}.tag.o{background:#fff;color:var(--ink);box-shadow:inset 0 0 0 1px var(--ink)}
.crumb{display:flex;gap:6px;align-items:center;flex-wrap:wrap;font-size:15px;padding:16px 0 0}.crumb a{color:var(--ink);text-decoration:underline;text-underline-offset:3px}.crumb svg{width:14px;height:14px;color:var(--sub)}
h1{font-size:44px;line-height:1.18;font-weight:800;letter-spacing:-.02em}h2{font-size:28px;line-height:1.3;font-weight:800;letter-spacing:-.01em}h3{font-size:20px;font-weight:700;line-height:1.4}
.cap{display:block;color:var(--sub);font-size:19px;font-weight:500;margin-bottom:6px}
.lead{font-size:21px;line-height:1.55;margin-top:18px;max-width:720px}
main{padding:28px 0 72px}.g{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:48px}.g>aside{padding-top:6px}
.sec{margin-top:52px}.sec>p.s{color:var(--sub);margin-top:6px;max-width:680px}
.btn{display:inline-flex;align-items:center;gap:8px;height:48px;padding:0 20px;background:var(--ok);color:#fff;font-weight:700;font-size:18px;box-shadow:0 2px 0 #0f3d26}.btn:hover{background:#185f3c}
.btn svg{width:20px;height:20px}.btn2{background:var(--soft);color:var(--ink);box-shadow:0 2px 0 #929191}.btn2:hover{background:#dbdad9}
.acts{display:flex;gap:16px;flex-wrap:wrap;margin-top:28px}
.start{margin-top:18px;border-top:1px solid var(--line)}.start a{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr) 24px;gap:20px;align-items:center;padding:16px 0;border-bottom:1px solid var(--line)}
.start a:hover b{text-decoration:underline}.start b{color:var(--ac);font-size:18px}.start span{color:var(--sub);font-size:15px}.start svg{color:var(--ac)}
/* 단계 안내: 번호와 세로 줄 */
.steps{margin-top:20px;list-style:none;padding:0}.steps>li{position:relative;padding:0 0 30px 56px}.steps>li::before{content:"";position:absolute;left:17px;top:38px;bottom:0;border-left:2px solid var(--line)}
.steps>li:last-child::before{display:none}.steps .n{position:absolute;left:0;top:0;width:36px;height:36px;border:2px solid var(--ink);border-radius:50%;display:grid;place-items:center;font-weight:800;background:#fff}
.steps h3{padding-top:4px}.steps h3 a{color:var(--ac);text-decoration:underline;text-underline-offset:3px}.steps p{color:var(--sub);margin-top:4px;max-width:640px}
.steps ul{margin:10px 0 0;padding:0 0 0 20px}.steps li li{margin:4px 0}.steps .meta{display:flex;gap:16px;flex-wrap:wrap;font-size:15px;color:var(--sub);margin-top:8px}
.steps .meta span{display:inline-flex;gap:6px;align-items:center}.steps .meta svg{width:16px;height:16px}
.box{border-left:6px solid var(--ac);background:var(--soft);padding:18px 22px}.box h3{font-size:18px}.box p{margin-top:6px;font-size:16px}
.side h3{font-size:18px;padding-top:12px;border-top:4px solid var(--ac)}.side ul{list-style:none;padding:0;margin:10px 0 0}.side li{margin:8px 0;font-size:16px}
.num{font-size:56px;font-weight:800;line-height:1;margin-top:12px;letter-spacing:-.02em}.num small{font-size:20px;margin-left:4px}
.kv{width:100%;border-collapse:collapse;margin-top:10px;font-size:16px}.kv th,.kv td{text-align:left;padding:10px 8px 10px 0;border-bottom:1px solid var(--line2);vertical-align:top}.kv th{font-weight:700;width:34%}
.kv td.r{text-align:right;font-variant-numeric:tabular-nums}
.news{list-style:none;padding:0;margin:16px 0 0;border-top:1px solid var(--line)}.news li{display:grid;grid-template-columns:108px 76px 1fr;gap:12px;padding:12px 0;border-bottom:1px solid var(--line);align-items:baseline}
.news time{color:var(--sub);font-size:15px;font-variant-numeric:tabular-nums}
.foot{border-top:2px solid var(--ac);background:var(--soft);padding:32px 0 40px;font-size:15px;color:var(--sub)}.foot b{color:var(--ink);font-size:16px}.foot p{margin-top:6px}.foot a{text-decoration:underline}
/* 주제와 챕터 */
.toc{list-style:none;padding:0;margin:12px 0 0}.toc li{padding:6px 0 6px 16px;position:relative}.toc li::before{content:"—";position:absolute;left:0;color:var(--sub)}
.toc a{color:var(--ac);text-decoration:underline;text-underline-offset:3px}
.lec{list-style:none;padding:0;margin:12px 0 0}.lec li{display:flex;gap:12px;align-items:baseline;padding:8px 0;border-bottom:1px solid #d4d4d4}.lec li:last-child{border:0}
.lec b{font-variant-numeric:tabular-nums;min-width:26px}.lec a{color:var(--ac);text-decoration:underline;text-underline-offset:3px}.lec small{color:var(--sub);margin-left:auto;white-space:nowrap}
.know{list-style:none;padding:0;margin:14px 0 0;border-top:1px solid var(--line)}.know li{display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:20px;padding:12px 0;border-bottom:1px solid var(--line);align-items:baseline}
.know .c{display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end}.know .c a{font-size:14px;color:var(--ac);text-decoration:underline}.know .c em{font-style:normal;font-size:14px;color:var(--sub)}
.prose{max-width:720px}.prose h2{margin:44px 0 12px;font-size:26px}.prose h3{margin:28px 0 8px}.prose p{margin:12px 0}.prose ul,.prose ol{padding-left:22px}.prose li{margin:6px 0}
.prose code,.know code{font-size:.88em;background:var(--soft);padding:1px 5px}.tw{overflow-x:auto;margin:16px 0}table{border-collapse:collapse;width:100%;font-size:16px}
.tw th,.tw td{text-align:left;vertical-align:top;padding:10px 12px 10px 0;border-bottom:1px solid var(--line)}.tw th{font-weight:700}
.pager{display:flex;justify-content:space-between;gap:24px;margin-top:56px;padding-top:20px;border-top:1px solid var(--line)}.pager a{display:block;max-width:48%}.pager small{display:flex;gap:6px;align-items:center;color:var(--sub);font-size:15px}
.pager b{color:var(--ac);text-decoration:underline;font-size:18px}.pager a.r{text-align:right;margin-left:auto}.pager a.r small{justify-content:flex-end}
.deck{position:relative;aspect-ratio:16/9;background:#000;margin-top:24px}.deck iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.dl{display:flex;gap:20px;flex-wrap:wrap;margin-top:12px;font-size:16px}.dl a{display:inline-flex;gap:6px;align-items:center;color:var(--ac);text-decoration:underline}.dl svg{width:18px;height:18px}
.parts{counter-reset:p;list-style:none;padding:0;margin:12px 0 0}.parts li{display:flex;gap:12px;padding:10px 0;border-bottom:1px solid var(--line2)}.parts li::before{counter-increment:p;content:counter(p);font-weight:800;min-width:20px}
.parts small{margin-left:auto;color:var(--sub);white-space:nowrap;font-variant-numeric:tabular-nums}
/* 사례 */
.filt fieldset{border:0;padding:0;margin:0 0 22px}.filt legend{font-weight:700;font-size:17px;margin-bottom:6px}.filt label{display:flex;gap:10px;align-items:center;padding:5px 0;font-size:16px;cursor:pointer}
.filt input{width:22px;height:22px;accent-color:var(--ink);margin:0}.res{border-top:1px solid var(--line)}.res article{padding:18px 0;border-bottom:1px solid var(--line)}
.res h3 a{color:var(--ac);text-decoration:underline;text-underline-offset:3px}.res dl{display:grid;grid-template-columns:auto 1fr;gap:2px 14px;margin:10px 0 0;font-size:15px}.res dt{color:var(--sub)}.res dd{margin:0}
.gf{grid-template-columns:240px minmax(0,1fr)}.fb{display:none}.count{display:flex;justify-content:space-between;align-items:center;font-size:19px;font-weight:700;margin-bottom:10px}.tabs{display:flex;gap:0;border-bottom:1px solid var(--line);margin-top:28px;overflow-x:auto}
.tabs a{padding:10px 16px;font-size:16px;white-space:nowrap;color:var(--ac);text-decoration:underline}.tabs a[aria-current]{color:var(--ink);text-decoration:none;font-weight:700;border:1px solid var(--line);border-bottom-color:#fff;margin-bottom:-1px;background:#fff}
${DLG_CSS({ scrim: "rgba(11,12,12,.55)", bg: "#fff", ink: "#0B0C0C", line: "#B1B4B6", sub: "#505A5F", r: "0", hover: "#F3F2F1" })}
@media (max-width:860px){.g,.gf{grid-template-columns:1fr;gap:36px}.filt{display:none}.fb{display:inline-flex;gap:8px;align-items:center;height:40px;padding:0 14px;border:2px solid var(--ink);background:#fff;font-size:16px;font-weight:700}.nav{display:none}h1{font-size:34px}.lead{font-size:19px}.know li{grid-template-columns:1fr;gap:6px}.know .c{justify-content:flex-start}
.start a{grid-template-columns:1fr 24px;gap:4px 12px}.start span{grid-column:1}.start svg{grid-row:1/3;grid-column:2}.news li{grid-template-columns:1fr;gap:2px}}
@media (max-width:640px){.w{padding:0 16px}.stl{display:none}.sbtn span{display:none}h2{font-size:24px}.pager{flex-direction:column}.pager a{max-width:none}}`;

const kit = kitFor();
const head = (cur) => `<header class="top"><div class="w"><a class="brand" href="home.html">${i("route")}${D.NAME}</a>
<nav class="nav" aria-label="메뉴">${MENU.map(([k, t, h]) => `<a href="${h}"${k === cur ? ' aria-current="page"' : ""}>${t}</a>`).join("")}</nav>
<a class="stl" href="home.html#start">시작하기</a><button class="sbtn" data-search>${i("search")}<span>찾기</span></button></div></header>
<div class="bar"><div class="w"><span class="tag">공개 로드맵</span><span>가입 없이 누구나 보는 공익 자료예요. 로드맵 ${S.version}, 강의 ${D.chapters.length}챕터</span></div></div>`;
const foot = `<footer class="foot"><div class="w"><b>${FOOT}</b>${LIC.map((l) => `<p>${l}</p>`).join("")}<p>고칠 곳이나 질문은 <a href="mailto:${D.CONTACT}">${D.CONTACT}</a>로 보내 주세요.</p></div></footer>`;
const crumb = (xs) => `<nav class="crumb" aria-label="현재 위치">${xs.map(([t, h], n) => (h ? `<a href="${h}">${t}</a>` : `<span>${t}</span>`) + (n < xs.length - 1 ? i("chevron-right") : "")).join("")}</nav>`;
const lecN = (s) => new Set(STAGE_LINKS[s.no]).size;

/* 홈 */
const home = html(D.NAME, css, `${head("")}<main><div class="w">
<div class="g"><div><span class="cap">AX 엔지니어 공개 로드맵</span><h1>AX 엔지니어가 되는 길을<br> 단계별로 안내해요</h1>
<p class="lead">${esc(S.defn)}</p>
<div class="acts"><a class="btn" href="#start">시작하기 ${i("arrow-right")}</a><a class="btn btn2" href="roadmap.html">로드맵 5단계 보기</a></div></div>
<aside class="side"><h3>이 사이트에서 볼 수 있는 것</h3><table class="kv"><tbody>${[["로드맵 단계", 5], ["기초 강의 챕터", D.chapters.length], ...LIB.slice(0, 4).map((l) => [l[1], l[2]])].map(([k, v]) => `<tr><th>${k}</th><td class="r">${v}</td></tr>`).join("")}</tbody></table></aside></div>
<section class="sec" id="start"><h2>나에게 맞는 시작점</h2><p class="s">지금 내 경험과 가까운 줄을 골라요. 어느 줄이든 가입 없이 바로 이어 볼 수 있어요.</p>
<div class="start">${S.start.map((r) => `<a href="roadmap.html"><b>${esc(r.who)}</b><span>첫 결과물: ${esc(r.first)}</span>${i("arrow-right")}</a>`).join("")}
<a href="chapter.html"><b>지금 수업을 듣고 있다</b><span>오늘 배운 챕터의 슬라이드와 PDF를 다시 봐요</span>${i("arrow-right")}</a></div></section>
<div class="g sec"><section><h2>로드맵 5단계</h2><p class="s">단계마다 읽을 문서와 다음 단계로 넘어가기 전에 스스로 확인할 질문이 있어요.</p>
<ol class="steps">${S.stages.map((s) => `<li><span class="n">${s.no}</span><h3><a href="roadmap.html">${esc(s.title)}</a></h3><p>${esc(D.firstSentence(s.lede))}</p>
<div class="meta"><span>${i("file-text")}${stageCount(s)}</span><span>${i("book-open")}${lecN(s) ? `이어진 기초 강의 ${lecN(s)}개` : "이어진 강의 없음"}</span></div></li>`).join("")}</ol></section>
<aside class="side"><h3>이번 달 채용 공고</h3><div class="num">${HIRE_TOTAL}<small>건</small></div><p style="color:var(--sub);font-size:15px;margin-top:8px">2026년 10월, 국내 AX·AI Agent·FDE</p>
<table class="kv"><tbody>${S.hiring.rows.map((r) => `<tr><th>${r.type}</th><td class="r">${r.n}건</td></tr>`).join("")}</tbody></table><p style="font-size:14px;color:var(--sub);margin-top:10px">${esc(S.hiring.note)}</p>
<h3 style="margin-top:36px">사례와 자료</h3><ul>${LIB.map((l) => `<li><a class="l" href="cases.html">${l[1]}</a> ${l[2]}개</li>`).join("")}</ul></aside></div>
<section class="sec" id="news"><h2>소식</h2><ul class="news">${NEWS.map(([d, k, t]) => `<li><time>${d}</time><span><span class="tag ${k === "강의" ? "g" : ""}">${k}</span></span><span>${t}</span></li>`).join("")}</ul></section>
</div></main>${foot}`, kit);

/* 로드맵 */
const roadmap = html("로드맵 · " + D.NAME, css, `${head("roadmap")}<main><div class="w">${crumb([["홈", "home.html"], ["로드맵"]])}
<div class="g" style="margin-top:20px"><div><span class="cap">로드맵 ${S.version}</span><h1>AX 엔지니어 로드맵</h1><p class="lead">${esc(S.stages[0].lede.split(". ")[0])}. 한 단계를 마치면 점검 질문으로 스스로 확인하고 다음 단계로 가요.</p></div>
<aside class="side"><h3>원문</h3><p style="font-size:16px;margin-top:8px">이 로드맵은 <a class="l" href="${D.GH("README.md")}">ax-engineer-roadmap</a> 레포를 그대로 옮겼어요. 사이트는 기초 강의 연결만 더해요.</p></aside></div>
<ol class="steps sec">${S.stages.map((s) => `<li><span class="n">${s.no}</span><h3><a href="topic.html">${esc(s.title)}</a></h3><p>${esc(s.lede)}</p>
<ul>${stageTopics(s).map((t, n) => `<li><a class="l" href="topic.html">${esc(t)}</a>${s.areas ? ` <span style="color:var(--sub);font-size:15px">${AREA_LINKS[s.areas[n].id].length ? `· 기초 강의 ${AREA_LINKS[s.areas[n].id].length}개` : ""}${SOON[s.areas[n].id] ? ` · 준비 중: ${SOON[s.areas[n].id]}` : ""}</span>` : ""}</li>`).join("")}</ul>
${s.checks.length ? `<div class="box" style="margin-top:14px"><h3>다음 단계로 가기 전에</h3>${s.checks.map((c) => `<p>${esc(c)}</p>`).join("")}</div>` : ""}</li>`).join("")}</ol>
</div></main>${foot}`, kit);

/* 로드맵 주제 */
const T = TOPIC;
const topic = html(T.title + " · 로드맵", css, `${head("roadmap")}<main><div class="w">${crumb([["홈", "home.html"], ["로드맵", "roadmap.html"], ["2단계 " + stageShort(T.stage.title), "roadmap.html"], [T.title]])}
<div class="g" style="margin-top:20px"><div><span class="cap">2단계 · 기술 기초 7영역 중 1</span><h1>${esc(T.title)}</h1><p class="lead">${esc(T.area.q)}</p>
<div class="box" style="margin-top:28px"><h3>먼저 익힐 기초 강의</h3><p>이 주제를 읽기 전에 손에 익혀 두면 좋은 챕터예요. 강의는 01부터 차례로 들어도 돼요.</p>
<ul class="lec">${T.lec.map((n) => `<li><b>${n}</b><a href="chapter.html">${esc(short(byNo[n].title))}</a><small>${byNo[n].track} · ${byNo[n].level}</small></li>`).join("")}</ul></div>
<section class="sec prose"><h2>왜 필요한가</h2><p>${esc(T.why)}</p></section>
<section class="sec"><h2>알아야 할 것</h2><p class="s">줄마다 이어진 강의가 오른쪽에 있어요. 이을 강의가 없는 줄은 "강의 준비 중"이에요.</p>
<ul class="know">${T.know.map((k) => `<li><span>${D.esc(k.t).replace(/`([^`]+)`/g, "<code>$1</code>")}</span><span class="c">${k.lec.length ? k.lec.map((n) => `<a href="chapter.html">${n} ${esc(short(byNo[n].title))}</a>`).join("") : "<em>강의 준비 중</em>"}</span></li>`).join("")}</ul></section>
<div class="prose">${T.body.o}</div>
<nav class="pager" aria-label="주제 이동"><a class="r" href="topic.html"><small>다음 주제 ${i("arrow-right")}</small><b>${esc(T.next.t)}</b></a></nav></div>
<aside class="side"><div style="position:sticky;top:20px"><h3>이 쪽의 내용</h3><ul class="toc"><li><a href="#">왜 필요한가</a></li><li><a href="#">알아야 할 것</a></li>${T.body.ids.map(([id, t]) => `<li><a href="#${id}">${esc(t)}</a></li>`).join("")}</ul>
<h3 style="margin-top:32px">관련 자료</h3><ul><li><a class="l" href="cases.html">업무 사례: ${esc(S.cases[2].t)}</a></li><li><a class="l" href="cases.html">템플릿: UI 통합 점검표</a></li></ul>
<h3 style="margin-top:32px">원문</h3><p style="font-size:15px;margin-top:8px"><a class="l" href="${D.GH(T.src)}">${T.src}</a><br>${S.version} · ${S.commit}</p></div></aside></div>
</div></main>${foot}`, kit);

/* 강의 챕터 */
const c = CH.c;
const chapter = html(c.title + " · 강의", css, `${head("lectures")}<main><div class="w">${crumb([["홈", "home.html"], ["강의", "chapter.html"], [`${c.stage}단계 ${c.stageTitle}`, "chapter.html"], [`${c.no} ${short(c.title)}`]])}
<div style="margin-top:20px"><span class="cap">강의 ${c.no} · ${c.track} · ${c.level}</span><h1>${esc(c.title)}</h1><p class="lead">${esc(c.goal.replace(/`/g, ""))}</p></div>
<div class="deck"><iframe src="${CH.deck}" title="${esc(c.title)} 슬라이드" loading="lazy"></iframe></div>
<div class="dl"><a href="${CH.deck}">${i("presentation")}슬라이드 크게 보기</a><a href="${CH.pdf}">${i("download")}PDF 받기</a><a href="#">${i("file-text")}챕터 README</a></div>
<div class="g sec"><div><h2>배우는 것</h2><ul class="prose" style="padding-left:22px;margin-top:12px">${CH.goals.map((g) => `<li>${esc(g).replace(/`([^`]+)`/g, "<code>$1</code>")}</li>`).join("")}</ul>
<h2 style="margin-top:48px">구성</h2><ol class="parts">${CH.parts.map((p) => `<li><span>${esc(p.p)}</span><small>${p.a}–${p.b}쪽</small></li>`).join("")}</ol></div>
<aside class="side"><h3>이 챕터를 쓰는 로드맵 주제</h3><ul>${CH.used.map((u) => `<li><a class="l" href="topic.html">${esc(u)}</a></li>`).join("")}</ul>
<h3 style="margin-top:32px">먼저 볼 챕터</h3><ul><li><a class="l" href="chapter.html">${CH.prev.no} ${esc(short(CH.prev.title))}</a></li></ul></aside></div>
<nav class="pager" aria-label="챕터 이동"><a href="chapter.html"><small>${i("arrow-left")}이전 챕터</small><b>${CH.prev.no} ${esc(short(CH.prev.title))}</b></a><a class="r" href="chapter.html"><small>다음 챕터 ${i("arrow-right")}</small><b>${CH.next.no} ${esc(short(CH.next.title))}</b></a></nav>
</div></main>${foot}`, kit);

/* 사례와 자료 */
const tabs = (cur) => `<nav class="tabs" aria-label="사례와 자료">${LIB.map(([k, t, n]) => `<a href="cases.html"${k === cur ? ' aria-current="page"' : ""}>${t} ${n}</a>`).join("")}</nav>`;
const cases = html("사례와 자료 · " + D.NAME, css, `${head("library")}<main><div class="w">${crumb([["홈", "home.html"], ["사례와 자료", "cases.html"], ["업무 사례"]])}
<div style="margin-top:20px"><span class="cap">사례와 자료</span><h1>업무 사례</h1><p class="lead">업무 하나를 원본 시스템, 승인 지점, 실패 대응까지 설계한 문서예요. 실제 조직의 성과가 아니라 공개 자료와 합성 데이터로 만든 설계예요.</p></div>
${tabs("cases")}
<div class="g gf" style="margin-top:32px"><form class="filt" aria-label="거르기"><fieldset><legend>업무 분야</legend>${AREAS.map((a) => `<label><input type="checkbox">${esc(a)}</label>`).join("")}</fieldset>
<fieldset><legend>난이도</legend>${[1, 2, 3, 4, 5].map((n) => `<label><input type="checkbox">${n}</label>`).join("")}</fieldset><fieldset><legend>근거</legend><label><input type="checkbox">실행 예제</label><label><input type="checkbox">설계 문서</label></fieldset></form>
<div><p class="count">사례 ${S.cases.length}개 · 추천 순서 <button class="fb">${i("list-checks")}거르기</button></p><div class="res">${S.cases.map((x) => `<article><h3><a href="cases.html">${esc(x.t)}</a></h3>
<dl><dt>분야</dt><dd>${esc(x.area)} · ${esc(x.industry)}</dd><dt>난이도</dt><dd>${x.diff} / 5 · 위험 ${esc(x.risk)}</dd><dt>쓰기 범위</dt><dd>${esc(x.scope)}</dd><dt>프로젝트</dt><dd>${esc(x.p)}</dd><dt>근거</dt><dd>${esc(x.ev)}</dd></dl></article>`).join("")}</div></div></div>
</div></main>${foot}`, kit);

for (const [f, h] of Object.entries({ home, roadmap, topic, chapter, cases })) write("v10", f + ".html", h);
console.log("v10 ok");
