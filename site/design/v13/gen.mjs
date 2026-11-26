// 시안 v13 · 자료실. 도서관 목록처럼 모든 것에 번호를 붙이고 표와 줄로 정리해요. 숫자는 두 레포에 실제로 있는 개수만 써요.
import * as D from "../plan/data.mjs";
const { i, esc, S, byNo, short, stageShort, TOPIC, CH, LIB, NEWS, MENU, FOOT, LIC, html, DLG_CSS, kitFor, stageTopics, stageCount, STAGE_LINKS, AREA_LINKS, SOON, HIRE_TOTAL, lecStages, indKo, STAGE_KO, VERIFY_KO } = D;
import { write } from "../lib.mjs";

const css = `:root{--bg:#F6F5F1;--card:#FFFFFF;--ink:#16181D;--sub:#5B6070;--mute:#8A8F9C;--line:#16181D;--hair:#D9D6CD;--ac:#2459C9}
body{background:var(--bg);color:var(--ink);font-size:16px;line-height:1.6}.w{max-width:1280px;margin:0 auto;padding:0 40px}
.mono,code,.code{font-family:"JetBrains Mono","D2Coding Hangul",monospace}
.top{border-bottom:1px solid var(--line)}.top .w{display:grid;grid-template-columns:3fr 6fr 3fr;align-items:center;height:56px;gap:20px}
.brand{white-space:nowrap;font-weight:800;font-size:16px;display:flex;gap:10px;align-items:baseline}.brand .code{font-size:12px;font-weight:500;color:var(--sub)}
.nav{display:flex;gap:24px;font-size:15px}.nav a{padding:4px 0}.nav a[aria-current]{box-shadow:inset 0 -2px 0 var(--ink);font-weight:700}.nav a:hover{color:var(--ac)}
.tr{display:flex;justify-content:flex-end;gap:16px;align-items:center;font-size:15px}.tr a{font-weight:700;display:flex;gap:6px;align-items:center}.tr a svg,.tr button svg{width:16px;height:16px}.tr button{border:0;background:none;cursor:pointer;display:flex;gap:6px;align-items:center;font-size:15px;color:var(--sub)}
.tr kbd{font-size:11px;border:1px solid var(--hair);padding:0 5px}
h1{font-size:56px;line-height:1.12;font-weight:800;letter-spacing:-.03em}h2{font-size:15px;font-weight:700;letter-spacing:.02em}h3{font-size:18px;font-weight:700}
.lab{font-family:"JetBrains Mono",monospace;font-size:12px;color:var(--sub);letter-spacing:.02em;text-transform:uppercase}
main{padding:56px 0 96px}.grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:0 24px}
.c3{grid-column:span 3}.c4{grid-column:span 4}.c5{grid-column:span 5}.c6{grid-column:span 6}.c7{grid-column:span 7}.c8{grid-column:span 8}.c9{grid-column:span 9}.c12{grid-column:span 12}
.lead{font-size:19px;color:var(--sub);margin-top:20px;max-width:620px}
.sec{margin-top:80px}.sh{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid var(--line);padding-bottom:10px}.sh a{font-size:14px;color:var(--sub)}.sh a:hover{color:var(--ac)}
/* 목록 */
.ix{border-top:2px solid var(--line);margin-top:40px}.ix a{display:grid;grid-template-columns:72px minmax(0,3fr) minmax(0,5fr) 120px 28px;gap:24px;align-items:baseline;padding:18px 0;border-bottom:1px solid var(--hair)}
.ix a:hover{background:var(--card)}.ix a:hover .t{color:var(--ac)}.ix .code{font-size:13px;color:var(--mute)}.ix .t{font-size:22px;font-weight:700;letter-spacing:-.01em}.ix p{color:var(--sub);font-size:15px}
.ix .n{font-size:40px;font-weight:800;text-align:right;letter-spacing:-.03em;line-height:1;font-variant-numeric:tabular-nums}.ix svg{width:20px;height:20px;align-self:center;color:var(--sub)}
.five{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));border-left:1px solid var(--hair);margin-top:18px}.five>*{border-right:1px solid var(--hair);padding:16px 18px 20px}.five.f3{grid-template-columns:repeat(3,minmax(0,1fr))}.five .code{font-size:12px;color:var(--mute)}
.five b{display:block;font-size:16px;margin-top:8px;line-height:1.45}.five p{font-size:14px;color:var(--sub);margin-top:8px}.five a:hover b{color:var(--ac)}
.rows{width:100%;border-collapse:collapse;font-size:15px}.rows th{font-family:"JetBrains Mono",monospace;font-size:11px;font-weight:500;color:var(--sub);text-transform:uppercase;letter-spacing:.04em;text-align:left;padding:10px 12px 10px 0;border-bottom:1px solid var(--line)}
.rows td{padding:12px 12px 12px 0;border-bottom:1px solid var(--hair);vertical-align:top}.rows td.code{font-size:13px;color:var(--mute);white-space:nowrap}.rows a:hover{color:var(--ac)}.rows .r{text-align:right;font-variant-numeric:tabular-nums}
.rows tr:hover td{background:var(--card)}
.pill{display:inline-block;font-size:12px;padding:0 7px;border:1px solid var(--hair);border-radius:3px;color:var(--sub);background:var(--card);white-space:nowrap}.pill.k{border-color:var(--ink);color:var(--ink)}
.ft{border-top:1px solid var(--line);padding:28px 0 48px;font-size:13px;color:var(--sub)}.ft .w{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:24px}.ft .a{grid-column:span 5}.ft .b{grid-column:span 7}.ft b{color:var(--ink)}.ft p{margin-top:4px}.ft a{text-decoration:underline}
/* 로드맵 열 */
.cols{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));border-top:2px solid var(--line);margin-top:40px}.col{border-right:1px solid var(--hair);padding:18px 18px 24px}.col:last-child{border:0}.col:first-child{padding-left:0}
.col .big{font-size:64px;font-weight:800;line-height:1;letter-spacing:-.04em}.col h3{margin-top:12px;min-height:52px}.col .m{font-size:13px;color:var(--sub);margin-top:4px}
.col ol{list-style:none;padding:0;margin:16px 0 0;border-top:1px solid var(--hair)}.col li a{display:grid;grid-template-columns:40px 1fr;gap:6px;padding:8px 0;border-bottom:1px solid var(--hair);font-size:14.5px;line-height:1.45}.col li a:hover{color:var(--ac)}.col li .code{font-size:11px;color:var(--mute);padding-top:3px}
.col .lk{font-size:12px;color:var(--sub);display:block;margin-top:2px}.col .chk{margin-top:16px;font-size:13px;color:var(--sub)}.col .chk p{margin-top:6px;padding-left:12px;border-left:2px solid var(--ink)}
/* 상세: 왼쪽 정보칸 */
.meta{position:sticky;top:24px;border-top:2px solid var(--line)}.meta dl{margin:0}.meta dt{font-family:"JetBrains Mono",monospace;font-size:11px;color:var(--mute);text-transform:uppercase;letter-spacing:.04em;padding-top:12px}.meta dd{margin:2px 0 0;padding-bottom:12px;border-bottom:1px solid var(--hair);font-size:15px}
.meta dd a{color:var(--ac);text-decoration:underline;text-underline-offset:3px}.meta .big{font-size:40px;font-weight:800;letter-spacing:-.03em;line-height:1.1}
.dt h1{font-size:48px}.q{font-size:22px;line-height:1.5;margin-top:18px;font-weight:500;max-width:760px}
.prose{max-width:760px}.prose h2{font-size:24px;letter-spacing:-.01em;margin:52px 0 12px;padding-top:12px;border-top:1px solid var(--line)}.prose h3{margin:26px 0 8px}.prose p{margin:12px 0}.prose ul,.prose ol{padding-left:22px}.prose li{margin:5px 0}.prose a{color:var(--ac);text-decoration:underline}
.prose code{font-size:.86em;background:#ECEAE3;padding:1px 4px}.tw{overflow-x:auto;margin:16px 0}.tw table{border-collapse:collapse;width:100%;font-size:15px}.tw th,.tw td{text-align:left;vertical-align:top;padding:9px 12px 9px 0;border-bottom:1px solid var(--hair)}.tw th{border-bottom-color:var(--line);font-size:13px}
.deck{position:relative;aspect-ratio:16/9;background:#111;margin-top:32px}.deck iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.acts{display:flex;gap:24px;margin-top:12px;font-size:15px}.acts a{display:flex;gap:6px;align-items:center;font-weight:700}.acts a:hover{color:var(--ac)}.acts svg{width:16px;height:16px}
.pg{display:grid;grid-template-columns:1fr 1fr;border-top:2px solid var(--line);margin-top:64px}.pg a{padding:16px 0}.pg a:hover b{color:var(--ac)}.pg .r{text-align:right;border-left:1px solid var(--hair)}.pg small{display:block;font-family:"JetBrains Mono",monospace;font-size:11px;color:var(--mute);text-transform:uppercase}.pg b{font-size:18px}
/* 자료실 목록 */
.tabs{display:flex;border-top:2px solid var(--line);border-bottom:1px solid var(--line);margin-top:40px;overflow-x:auto}.tabs a{padding:12px 20px 12px 0;margin-right:20px;font-size:15px;white-space:nowrap;color:var(--sub)}.tabs a b{color:var(--ink);font-variant-numeric:tabular-nums;margin-left:6px}.tabs a[aria-current]{color:var(--ink);font-weight:700;box-shadow:inset 0 -3px 0 var(--ink)}
.facet{border-top:1px solid var(--line);padding-top:10px;margin-bottom:28px}.facet h2{font-family:"JetBrains Mono",monospace;font-size:11px;font-weight:500;color:var(--sub);text-transform:uppercase;letter-spacing:.04em}
.facet label{display:flex;gap:10px;align-items:center;padding:5px 0;font-size:15px;cursor:pointer}.facet input{margin:0;width:16px;height:16px;accent-color:var(--ink)}.facet label span{margin-left:auto;font-variant-numeric:tabular-nums;color:var(--mute);font-size:13px}
.cnt{display:flex;justify-content:space-between;align-items:baseline;padding-bottom:10px}.cnt b{font-size:28px;letter-spacing:-.02em}.cnt span{font-size:14px;color:var(--sub)}
.note{font-size:13px;color:var(--sub);margin-top:16px;padding-left:12px;border-left:2px solid var(--ink)}
${DLG_CSS({ scrim: "rgba(22,24,29,.45)", bg: "#fff", ink: "#16181D", line: "#D9D6CD", sub: "#5B6070", r: "0", hover: "#F6F5F1" })}
@media (max-width:1100px){.cols{grid-template-columns:repeat(3,minmax(0,1fr))}.col{border-bottom:1px solid var(--hair)}.col:first-child{padding-left:18px}.five{grid-template-columns:repeat(3,minmax(0,1fr))}.five>*{border-bottom:1px solid var(--hair)}}
@media (max-width:860px){.w{padding:0 20px}.top .w{grid-template-columns:1fr auto}.nav{display:none}.grid>*{grid-column:span 12}h1{font-size:38px}.dt h1{font-size:34px}.q{font-size:19px}
.ix a{grid-template-columns:52px minmax(0,1fr) auto;gap:4px 14px}.ix p{grid-column:2/4}.ix svg{display:none}.ix .n{font-size:30px;grid-row:1;grid-column:3}.ix .t{font-size:19px}
.cols{grid-template-columns:1fr}.col{padding:18px 0!important;border-right:0}.col h3{min-height:0}.five,.five.f3{grid-template-columns:1fr 1fr}.meta{position:static;margin-bottom:32px}.ft .a,.ft .b{grid-column:span 12}.hide-m{display:none}}
@media (max-width:520px){.brand .code{display:none}.w{padding:0 16px}.tr .tx{display:none}.five,.five.f3{grid-template-columns:1fr}.rows{font-size:14px}}`;

const kit = kitFor();
const head = (cur) => `<header class="top"><div class="w"><a class="brand" href="home.html">${D.NAME}<span class="code">공개 자료실</span></a>
<nav class="nav" aria-label="메뉴">${MENU.map(([k, t, h]) => `<a href="${h}"${k === cur ? ' aria-current="page"' : ""}>${t}</a>`).join("")}</nav>
<div class="tr"><button data-search>${i("search")}<span class="tx">찾기</span><kbd>/</kbd></button><a href="home.html#start">시작하기 ${i("arrow-right")}</a></div></div></header>`;
const foot = `<footer class="ft"><div class="w"><div class="a"><b>${FOOT}</b><p>고칠 곳과 질문: <a href="mailto:${D.CONTACT}">${D.CONTACT}</a></p></div><div class="b">${LIC.map((l) => `<p>${l}</p>`).join("")}</div></div></footer>`;
const CODE = { roadmap: "R", lectures: "L", cases: "C", public: "K/G", failures: "F", templates: "T", jobs: "J" };

/* 홈 */
const IX = [
  ["R", "로드맵", "roadmap.html", `${S.stages.length}단계, 주제 25개. 단계마다 읽을 문서와 넘어가기 전 점검 질문`, 25, "주제"],
  ["L", "기초 강의", "chapter.html", "터미널부터 데이터 분석까지 배우는 순서대로. 슬라이드, PDF, 실습", D.chapters.length, "챕터"],
  ...LIB.map(([k, t, n, d]) => [CODE[k], t, "cases.html", d, n, k === "jobs" ? "건" : "개"]),
];
const home = html(D.NAME, css, `${head("")}<main><div class="w">
<div class="grid"><div class="c8"><span class="lab">AX 엔지니어 공개 자료실 · 로드맵 ${S.version} · 강의 ${D.chapters.length}챕터</span><h1 style="margin-top:16px">AX 엔지니어가 알아야 할 것을 한곳에 모아 번호를 붙였어요</h1></div>
<div class="c4" style="align-self:end"><p class="lead" style="margin-top:0">${esc(S.defn)}</p></div></div>
<div class="ix" aria-label="자료 목록">${IX.map(([c, t, h, d, n, u]) => `<a href="${h}"><span class="code">${c}</span><span class="t">${t}</span><p>${esc(d)}</p><span class="n">${n}<small style="font-size:14px;font-weight:500;margin-left:3px">${u}</small></span>${i("arrow-right")}</a>`).join("")}</div>
<section class="sec" id="start"><div class="sh"><h2>나에게 맞는 시작점</h2><span class="lab">S1–S6</span></div>
<div class="five f3">${S.start.map((r, n) => `<a href="roadmap.html"><span class="code">S${n + 1}</span><b>${esc(r.who)}</b><p>${esc(r.go)}</p></a>`).join("")}<a href="chapter.html"><span class="code">S6</span><b>지금 수업을 듣고 있다</b><p>강의 챕터에서 슬라이드와 PDF를 다시 봐요</p></a></div></section>
<div class="grid sec"><section class="c7" id="news"><div class="sh"><h2>소식</h2><a href="#">전체 보기</a></div>
<table class="rows"><tbody>${NEWS.map(([d, k, t]) => `<tr><td class="code">${d}</td><td><span class="pill ${k === "로드맵" ? "k" : ""}">${k}</span></td><td>${t}</td></tr>`).join("")}</tbody></table></section>
<section class="c5"><div class="sh"><h2>채용 공고 · 2026년 10월</h2><span class="lab">J</span></div><table class="rows"><thead><tr><th>유형</th><th class="r">공고</th><th class="r">모집 중</th></tr></thead><tbody>${S.hiring.rows.map((r) => `<tr><td>${r.type}</td><td class="r">${r.n}</td><td class="r">${r.open}</td></tr>`).join("")}<tr><td><b>합계</b></td><td class="r"><b>${HIRE_TOTAL}</b></td><td class="r"><b>${S.hiring.rows.reduce((a, r) => a + r.open, 0)}</b></td></tr></tbody></table>
<p class="note">${esc(S.hiring.note)}</p></section></div>
<section class="sec"><div class="sh"><h2>자료를 고르는 원칙</h2><a href="#">이 사이트에 대해</a></div><div class="five f3">
<div><span class="code">01</span><b>실행 예제와 설계 문서를 나눠요</b><p>돌려 볼 수 있는 예제는 1개, 나머지 업무 사례는 실행 전 설계라고 표시해요.</p></div>
<div><span class="code">02</span><b>외부 발표는 주장마다 출처를 달아요</b><p>공개 사례는 회사가 밝힌 내용과 교차 확인한 내용을 구분하고 확인일을 적어요.</p></div>
<div><span class="code">03</span><b>강의 출력은 실제로 실행한 화면이에요</b><p>슬라이드의 터미널과 SQL 결과는 지어내지 않고 실행해서 옮겼어요.</p></div></div></section>
</div></main>${foot}`, kit);

/* 로드맵 */
const roadmap = html("로드맵 · " + D.NAME, css, `${head("roadmap")}<main><div class="w">
<div class="grid"><div class="c8"><span class="lab">R · 로드맵 ${S.version} · 원문 ax-engineer-roadmap</span><h1 style="margin-top:16px">AX 엔지니어 로드맵</h1></div><div class="c4" style="align-self:end"><p class="lead" style="margin:0">다섯 열을 왼쪽부터 차례로 읽어요. 각 주제 아래 작은 글씨는 이어진 기초 강의 번호예요.</p></div></div>
<div class="cols">${S.stages.map((s) => `<section class="col"><span class="big">${s.no}</span><h3>${esc(s.title)}</h3><p class="m">${stageCount(s)}</p>
<ol>${stageTopics(s).map((t, n) => { const id = s.areas?.[n]?.id; const ls = id ? AREA_LINKS[id] : []; return `<li><a href="topic.html"><span class="code">R${s.no}.${n + 1}</span><span>${esc(t)}${ls.length ? `<span class="lk mono">L ${ls.join(" ")}</span>` : id ? `<span class="lk">강의 준비 중</span>` : ""}</span></a></li>`; }).join("")}</ol>
${s.checks.length ? `<div class="chk"><span class="lab">점검</span>${s.checks.map((c) => `<p>${esc(c)}</p>`).join("")}</div>` : ""}</section>`).join("")}</div>
</div></main>${foot}`, kit);

/* 로드맵 주제 */
const T = TOPIC;
const topic = html(T.title + " · 로드맵", css, `${head("roadmap")}<main><div class="w"><div class="grid">
<aside class="c3"><div class="meta"><dl><dt>번호</dt><dd class="big">R2.1</dd><dt>단계</dt><dd><a href="roadmap.html">2 · ${esc(T.stage.title)}</a></dd><dt>이어진 강의</dt><dd>${T.lec.length}챕터 · 준비 중 ${T.know.filter((k) => !k.lec.length).length}항목</dd>
<dt>관련 자료</dt><dd><a href="cases.html">C3 ${esc(S.cases[2].t)}</a><br><a href="cases.html">T UI 통합 점검표</a></dd><dt>원문</dt><dd class="mono" style="font-size:12px;word-break:break-all"><a href="${D.GH(T.src)}">${T.src}</a></dd><dt>판</dt><dd class="mono" style="font-size:13px">${S.version} · ${S.commit}</dd>
<dt>이 쪽의 내용</dt><dd>${["왜 필요한가", "알아야 할 것", ...T.body.ids.map((x) => x[1])].map((t) => `<a href="#" style="display:block;text-decoration:none;color:var(--ink);padding:2px 0">${esc(t)}</a>`).join("")}</dd></dl></div></aside>
<article class="c9 dt"><span class="lab">로드맵 · 기술 기초 7영역</span><h1 style="margin-top:12px">${esc(T.title)}</h1><p class="q">${esc(T.area.q)}</p>
<section style="margin-top:44px"><div class="sh"><h2>먼저 익힐 기초 강의</h2><span class="lab">L · ${T.lec.length}</span></div>
<table class="rows"><tbody>${T.lec.map((n) => `<tr><td class="code">L${n}</td><td><a href="chapter.html">${esc(byNo[n].title)}</a></td><td class="hide-m" style="color:var(--sub)">${byNo[n].track}</td><td class="r" style="color:var(--sub)">${byNo[n].level}</td></tr>`).join("")}</tbody></table></section>
<div class="prose"><h2>왜 필요한가</h2><p>${esc(T.why)}</p><h2>알아야 할 것</h2></div>
<table class="rows" style="max-width:760px"><thead><tr><th style="width:44px">#</th><th>항목</th><th class="r">강의</th></tr></thead><tbody>${T.know.map((k, n) => `<tr><td class="code">${n + 1}</td><td>${esc(k.t)}</td><td class="r mono" style="font-size:13px;white-space:nowrap">${k.lec.length ? k.lec.map((x) => `<a href="chapter.html">L${x}</a>`).join(" ") : `<span style="color:var(--mute)">준비 중</span>`}</td></tr>`).join("")}</tbody></table>
<div class="prose">${T.body.o}</div>
<nav class="pg" aria-label="주제 이동"><a href="roadmap.html"><small>목록</small><b>로드맵 2단계</b></a><a class="r" href="topic.html"><small>다음 · R2.2</small><b>${esc(T.next.t)}</b></a></nav></article></div>
</div></main>${foot}`, kit);

/* 강의 챕터 */
const c = CH.c;
const chapter = html(c.title + " · 강의", css, `${head("lectures")}<main><div class="w"><div class="grid">
<aside class="c3"><div class="meta"><dl><dt>번호</dt><dd class="big">L${c.no}</dd><dt>강의 단계</dt><dd>${c.stage} · ${esc(c.stageTitle)}</dd><dt>분류 · 수준</dt><dd>${c.track} · ${c.level}</dd><dt>슬라이드</dt><dd>${CH.slides.length}쪽 · <a href="${CH.pdf}">PDF</a></dd>
<dt>먼저 볼 챕터</dt><dd><a href="chapter.html">L${CH.prev.no} ${esc(short(CH.prev.title))}</a></dd><dt>쓰는 로드맵 주제</dt><dd>${CH.used.map((u) => `<a href="topic.html">R2.1 ${esc(u)}</a>`).join("<br>")}</dd><dt>원본</dt><dd class="mono" style="font-size:12px">${c.dir}/</dd></dl></div></aside>
<article class="c9 dt"><span class="lab">강의 · ${esc(c.stageTitle)}</span><h1 style="margin-top:12px">${esc(c.title)}</h1><p class="q">${esc(c.goal.replace(/`/g, ""))}</p>
<div class="deck"><iframe src="${CH.deck}" title="${esc(c.title)} 슬라이드" loading="lazy"></iframe></div><div class="acts"><a href="${CH.deck}">${i("presentation")}크게 보기</a><a href="${CH.pdf}">${i("download")}PDF 받기</a></div>
<div class="grid" style="margin-top:48px"><section class="c6"><div class="sh"><h2>배우는 것</h2></div><table class="rows"><tbody>${CH.goals.map((g, n) => `<tr><td class="code">${n + 1}</td><td>${esc(g).replace(/`([^`]+)`/g, "<code>$1</code>")}</td></tr>`).join("")}</tbody></table></section>
<section class="c6"><div class="sh"><h2>구성</h2><span class="lab">${CH.parts.length} 파트</span></div><table class="rows"><tbody>${CH.parts.map((p, n) => `<tr><td class="code">P${n + 1}</td><td>${esc(p.p)}</td><td class="r code">${p.a}–${p.b}</td></tr>`).join("")}</tbody></table></section></div>
<nav class="pg" aria-label="챕터 이동"><a href="chapter.html"><small>이전 · L${CH.prev.no}</small><b>${esc(short(CH.prev.title))}</b></a><a class="r" href="chapter.html"><small>다음 · L${CH.next.no}</small><b>${esc(short(CH.next.title))}</b></a></nav></article></div>
</div></main>${foot}`, kit);

/* 사례와 자료: 공개 AX 사례 목록 */
const P = S.publicCases.list;
const cnt = (f) => Object.entries(P.reduce((a, x) => ((a[f(x)] = (a[f(x)] || 0) + 1), a), {})).sort((a, b) => b[1] - a[1]);
const facet = (t, xs) => `<div class="facet"><h2>${t}</h2>${xs.map(([k, n]) => `<label><input type="checkbox">${esc(k)}<span>${n}</span></label>`).join("")}</div>`;
const cases = html("사례와 자료 · " + D.NAME, css, `${head("library")}<main><div class="w">
<div class="grid"><div class="c8"><span class="lab">사례와 자료</span><h1 style="margin-top:16px">공개 AX 사례</h1></div><div class="c4" style="align-self:end"><p class="lead" style="margin:0">회사와 기관이 직접 밝힌 AX 도입 기록이에요. 주장마다 출처와 확인일을 달았고, 성과를 교차 확인했는지 따로 표시해요.</p></div></div>
<nav class="tabs" aria-label="자료 묶음">${LIB.map(([k, t, n]) => `<a href="cases.html"${k === "public" ? ' aria-current="page"' : ""}>${t}<b>${n}</b></a>`).join("")}</nav>
<div class="grid" style="margin-top:32px"><aside class="c3 hide-m">${facet("지역", cnt((x) => (x.region === "KR" ? "국내" : "해외")))}${facet("도입 단계", cnt((x) => STAGE_KO[x.stage] || x.stage))}${facet("성과 검증", cnt((x) => VERIFY_KO[x.verify] || x.verify))}${facet("산업 (상위 6)", cnt((x) => indKo(x.ind)).slice(0, 6))}</aside>
<section class="c9"><div class="cnt"><b>${P.length}개</b><span>국내 ${S.publicCases.kr} · 해외 ${P.length - S.publicCases.kr}</span></div>
<table class="rows"><thead><tr><th>번호</th><th>조직</th><th>바꾼 업무</th><th class="hide-m">산업</th><th class="hide-m">단계</th><th class="hide-m">검증</th></tr></thead><tbody>${P.slice(0, 20).map((x) => `<tr><td class="code">${x.id}</td><td><a href="cases.html"><b>${esc(x.org)}</b></a></td><td>${esc(x.w)}</td><td class="hide-m" style="color:var(--sub)">${esc(indKo(x.ind))}</td><td class="hide-m"><span class="pill">${STAGE_KO[x.stage] || x.stage}</span></td><td class="hide-m"><span class="pill ${x.verify === "cross-checked" ? "k" : ""}">${VERIFY_KO[x.verify] || x.verify}</span></td></tr>`).join("")}</tbody></table>
<p class="note">20개까지 보여 줘요. 원문은 ax-engineer-roadmap의 research/public-ax-cases.json이에요. 자체 발표는 회사가 밝힌 숫자를 그대로 옮긴 것이라 독립 검증이 아니에요.</p></section></div>
</div></main>${foot}`, kit);

for (const [f, h] of Object.entries({ home, roadmap, topic, chapter, cases })) write("v13", f + ".html", h);
console.log("v13 ok");
