// 시안 v12 · 핸드북. 개발 문서 사이트처럼 왼쪽 목차, 가운데 본문, 오른쪽 쪽 안 목차를 둬요. 찾기가 가장 앞에 있어요.
import * as D from "../plan/data.mjs";
const { i, esc, S, byNo, short, stageShort, TOPIC, CH, LIB, NEWS, MENU, FOOT, LIC, html, DLG_CSS, kitFor, AREAS, stageTopics, stageCount, STAGE_LINKS, AREA_LINKS, SOON, HIRE_TOTAL, lecStages } = D;
import { write } from "../lib.mjs";

const css = `:root{--bg:#fff;--side:#FAFAF9;--ink:#1D2330;--sub:#5F6675;--mute:#9298A4;--line:#EAE9E6;--line2:#D9D7D2;--ac:#2459C9;--ac-s:#EEF3FD;--code:#F4F3F0}
body{background:var(--bg);color:var(--ink);font-size:16px;line-height:1.65}
.top{height:60px;border-bottom:1px solid var(--line);display:grid;grid-template-columns:280px minmax(0,1fr) auto;align-items:center;position:sticky;top:0;background:#fff;z-index:5}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;padding:0 20px;font-size:16px}.brand .mk{width:26px;height:26px;border-radius:7px;background:var(--ink);color:#fff;display:grid;place-items:center}.brand .mk svg{width:16px;height:16px}
.sf{display:flex;align-items:center;gap:10px;max-width:520px;width:100%;height:40px;padding:0 12px;border:1px solid var(--line2);border-radius:8px;background:var(--side);color:var(--mute);font-size:15px;cursor:pointer;margin-left:24px;text-align:left}
.sf span{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sf kbd{font-size:12px;border:1px solid var(--line2);border-radius:5px;padding:1px 6px;background:#fff;color:var(--sub)}
.tn{display:flex;gap:2px;padding:0 20px}.tn a{padding:7px 11px;border-radius:7px;font-size:15px;font-weight:600;color:var(--sub)}.tn a:hover{background:var(--side);color:var(--ink)}.tn a[aria-current]{color:var(--ac)}
.tn a.st{background:var(--ac);color:#fff;margin-left:8px}
.shell{display:grid;grid-template-columns:280px minmax(0,1fr)}
.side{border-right:1px solid var(--line);background:var(--side);position:sticky;top:60px;height:calc(100vh - 60px);overflow:auto;padding:20px 12px 40px;font-size:14.5px}
.side h4{font-size:12px;font-weight:700;color:var(--mute);letter-spacing:.04em;margin:22px 10px 6px}.side h4:first-child{margin-top:0}
.side a{display:flex;gap:8px;align-items:baseline;padding:5px 10px;border-radius:6px;color:var(--sub);line-height:1.45}.side a:hover{background:#F0EFEB;color:var(--ink)}.side a.on{background:var(--ac-s);color:var(--ac);font-weight:700}
.side a .n{font-family:"JetBrains Mono",monospace;font-size:12px;color:var(--mute);min-width:18px}.side .sub{margin-left:18px;border-left:1px solid var(--line2);padding-left:6px}.side .sub a{font-size:14px}
.side a .c{margin-left:auto;font-size:12px;color:var(--mute)}
.main{display:grid;grid-template-columns:minmax(0,1fr) 220px;gap:48px;padding:36px 48px 80px;max-width:1240px}.main.wide{grid-template-columns:minmax(0,1fr)}
.crumb{display:flex;gap:6px;align-items:center;font-size:14px;color:var(--mute);flex-wrap:wrap}.crumb a:hover{color:var(--ac)}.crumb svg{width:14px;height:14px}
h1{font-size:36px;line-height:1.25;font-weight:800;letter-spacing:-.02em;margin-top:10px}h2{font-size:24px;line-height:1.35;font-weight:800;letter-spacing:-.01em}h3{font-size:17px;font-weight:700}
.desc{font-size:18px;color:var(--sub);margin-top:10px;max-width:760px}.metal{display:flex;gap:16px;flex-wrap:wrap;margin-top:14px;font-size:13px;color:var(--mute)}.metal span,.metal a{display:flex;gap:6px;align-items:center}.metal svg{width:15px;height:15px}.metal a:hover{color:var(--ac)}
.mono,code{font-family:"JetBrains Mono","D2Coding Hangul",monospace}
code{font-size:.86em;background:var(--code);padding:1px 5px;border-radius:4px}
.call{display:grid;grid-template-columns:22px minmax(0,1fr);gap:12px;border:1px solid #C9D7F5;background:var(--ac-s);border-radius:10px;padding:16px 18px;margin-top:24px}.call>svg{color:var(--ac);margin-top:3px}.call h3{font-size:16px}.call p{font-size:14.5px;color:var(--sub)}
table{border-collapse:collapse;width:100%;font-size:15px}.tbl{border:1px solid var(--line);border-radius:10px;overflow:hidden;margin-top:14px}.tbl th,.tbl td{text-align:left;vertical-align:top;padding:10px 14px;border-bottom:1px solid var(--line)}
.tbl tr:last-child td{border-bottom:0}.tbl th{background:var(--side);font-size:13px;color:var(--sub);font-weight:700}.tbl td.n{font-family:"JetBrains Mono",monospace;font-size:13px;color:var(--sub);width:48px}.tbl a{color:var(--ac)}.tbl a:hover{text-decoration:underline}
.tbl .r{text-align:right;font-variant-numeric:tabular-nums}.tbl small{color:var(--mute)}
.call .tbl{background:#fff;margin-top:10px}
.prose{max-width:780px}.prose h2{margin:44px 0 10px;padding-top:12px;border-top:1px solid var(--line)}.prose h3{margin:24px 0 6px}.prose p{margin:10px 0}.prose ul,.prose ol{padding-left:22px}.prose li{margin:4px 0}.prose a{color:var(--ac)}.prose a:hover{text-decoration:underline}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:10px;margin:14px 0}.tw th,.tw td{text-align:left;vertical-align:top;padding:9px 12px;border-bottom:1px solid var(--line)}.tw th{background:var(--side);font-size:13px}.tw tr:last-child td{border:0}
.lec{display:inline-flex;gap:4px;flex-wrap:wrap}.lec a{font-family:"JetBrains Mono",monospace;font-size:12px;padding:1px 6px;border-radius:4px;background:var(--code);color:var(--ink)}.lec a:hover{background:var(--ac-s);color:var(--ac)}.lec em{font-style:normal;font-size:13px;color:var(--mute)}
.otp{position:sticky;top:96px;align-self:start;font-size:13.5px}.otp h4{font-size:12px;color:var(--mute);font-weight:700;letter-spacing:.04em;margin-bottom:8px}.otp a{display:block;padding:4px 0;color:var(--sub)}.otp a:hover{color:var(--ac)}.otp a.on{color:var(--ac);font-weight:700}
.otp .blk{margin-top:22px;padding-top:16px;border-top:1px solid var(--line)}
.pn{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:48px}.pn a{border:1px solid var(--line);border-radius:10px;padding:14px 16px}.pn a:hover{border-color:var(--ac)}.pn small{display:block;font-size:13px;color:var(--mute)}.pn b{color:var(--ac)}.pn .r{text-align:right;grid-column:2}
.edit{display:flex;gap:6px;align-items:center;font-size:13px;color:var(--mute);margin-top:28px}.edit svg{width:15px;height:15px}.edit a{color:var(--sub);text-decoration:underline}
/* 홈 */
.hs{max-width:860px}.bigs{display:flex;align-items:center;gap:12px;height:56px;padding:0 18px;border:1px solid var(--line2);border-radius:12px;font-size:17px;color:var(--mute);margin-top:24px;cursor:pointer;background:#fff;width:100%;text-align:left;box-shadow:0 1px 2px rgba(0,0,0,.04)}.bigs span{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bigs kbd{font-size:13px;border:1px solid var(--line2);border-radius:6px;padding:2px 8px;color:var(--sub)}.hint{font-size:13px;color:var(--mute);margin-top:10px}.hint code{font-size:12px}
.ix{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:36px}.ixb{border:1px solid var(--line);border-radius:12px;padding:18px 20px}.ixb h2{font-size:17px;display:flex;gap:8px;align-items:center}.ixb h2 svg{color:var(--ac)}
.ixb p{font-size:14px;color:var(--sub);margin-top:2px}.ixb ul{list-style:none;margin:12px 0 0;padding:0}.ixb li a{display:flex;gap:10px;padding:6px 0;border-top:1px solid var(--line);font-size:15px}.ixb li a:hover{color:var(--ac)}.ixb li .n{font-family:"JetBrains Mono",monospace;color:var(--mute);font-size:12px;min-width:30px;padding-top:2px}.ixb li .c{margin-left:auto;color:var(--mute);font-size:13px;white-space:nowrap}
.chg{list-style:none;margin:12px 0 0;padding:0}.chg li{display:grid;grid-template-columns:96px 64px 1fr;gap:12px;padding:9px 0;border-top:1px solid var(--line);font-size:15px}.chg time{font-family:"JetBrains Mono",monospace;font-size:13px;color:var(--mute)}
.badge{font-size:12px;font-weight:700;color:var(--sub);border:1px solid var(--line2);border-radius:5px;padding:0 6px;justify-self:start;height:22px;line-height:20px}.badge.r{color:var(--ac);border-color:#C9D7F5;background:var(--ac-s)}
.ft{border-top:1px solid var(--line);padding:24px 48px 40px;font-size:13px;color:var(--mute)}.ft b{color:var(--sub)}.ft p{margin-top:3px}.ft a{text-decoration:underline}
.deck{position:relative;aspect-ratio:16/9;border-radius:10px;overflow:hidden;background:#111;margin-top:22px;border:1px solid var(--line)}.deck iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.tabsx{display:flex;gap:2px;border-bottom:1px solid var(--line);margin-top:28px;overflow-x:auto}.tabsx a{padding:9px 14px;font-size:15px;color:var(--sub);white-space:nowrap}.tabsx a[aria-current]{color:var(--ink);font-weight:700;box-shadow:inset 0 -2px 0 var(--ac)}
.btns{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}.btns a{display:flex;align-items:center;gap:7px;height:36px;padding:0 13px;border:1px solid var(--line2);border-radius:8px;font-size:14px;font-weight:600}.btns a:hover{border-color:var(--ac);color:var(--ac)}.btns svg{width:16px;height:16px}
.fl{display:flex;gap:8px;flex-wrap:wrap;margin-top:20px}.sel{display:flex;align-items:center;gap:6px;height:34px;padding:0 10px 0 12px;border:1px solid var(--line2);border-radius:8px;font-size:14px;color:var(--sub);background:#fff}.sel svg{width:15px;height:15px}
.diff{display:inline-flex;gap:2px}.diff i{width:7px;height:12px;border-radius:2px;background:var(--line2);display:block}.diff i.on{background:var(--ink)}
.mtg{display:none}
${DLG_CSS({ scrim: "rgba(29,35,48,.4)", bg: "#fff", ink: "#1D2330", line: "#EAE9E6", sub: "#5F6675", r: "12px", hover: "#F4F3F0" })}
@media (max-width:1180px){.main{grid-template-columns:minmax(0,1fr);padding:32px 32px 72px}.otp{display:none}.tn a:not(.st){display:none}}
@media (max-width:860px){.top{grid-template-columns:auto minmax(0,1fr) auto}.side{display:none}.shell{grid-template-columns:1fr}.sf{margin-left:0}.sf kbd,.brand b{display:none}.mtg{display:grid;place-items:center;width:40px;height:40px;margin-left:8px;border:0;background:none}
.ix{grid-template-columns:1fr}.main{padding:24px 16px 64px}h1{font-size:28px}.ft{padding:24px 16px 40px}.pn{grid-template-columns:1fr}.pn .r{grid-column:1}.chg li{grid-template-columns:90px 1fr}.chg li .badge{display:none}.tn{padding:0 12px 0 8px}.brand{padding:0 0 0 12px}
.hide-m{display:none}}`;

const kit = kitFor();
const side = (on) => `<nav class="side" aria-label="전체 목차">
<h4>시작</h4><a href="home.html"${on === "home" ? ' class="on"' : ""}>처음 오셨나요</a><a href="home.html#start">나에게 맞는 시작점</a><a href="#">용어 사전</a>
<h4>로드맵 ${S.version}</h4>${S.stages.map((s) => `<a href="roadmap.html"${on === "roadmap" && s.no === 1 ? "" : ""}><span class="n">${s.no}</span>${esc(stageShort(s.title))}</a>${s.no === 2 && on === "topic" ? `<div class="sub">${s.areas.map((a, n) => `<a href="topic.html"${n === 0 ? ' class="on"' : ""}>${esc(a.t)}</a>`).join("")}</div>` : ""}`).join("")}
<h4>강의 · ${D.chapters.length}챕터</h4>${lecStages.map((s) => `<a href="chapter.html"><span class="n">${s.from}</span>${esc(s.title)}<span class="c">${s.list.length}</span></a>${on === "chapter" && s.no === 4 ? `<div class="sub">${s.list.map((c) => `<a href="chapter.html"${c.no === "36" ? ' class="on"' : ""}><span class="n">${c.no}</span>${esc(short(c.title))}</a>`).join("")}</div>` : ""}`).join("")}
<a href="chapter.html"><span class="n">+</span>꿀팁 (번외)<span class="c">${D.extras.length}</span></a>
<h4>사례와 자료</h4>${LIB.map(([k, t, n]) => `<a href="cases.html"${on === "cases" && k === "cases" ? ' class="on"' : ""}>${t}<span class="c">${n}</span></a>`).join("")}<a href="#">조직 성숙도</a>
<h4>그 밖</h4><a href="home.html#news">소식</a><a href="#">이 사이트에 대해</a></nav>`;
const top = (cur) => `<header class="top"><a class="brand" href="home.html"><span class="mk">${i("book-open")}</span><b>${D.NAME}</b></a>
<button class="sf" data-search>${i("search")}<span>주제, 챕터, 명령어, 사례 찾기</span><kbd>/</kbd></button>
<nav class="tn" aria-label="메뉴">${MENU.map(([k, t, h]) => `<a href="${h}"${k === cur ? ' aria-current="page"' : ""}>${t}</a>`).join("")}<a class="st" href="home.html#start">시작하기</a><button class="mtg" aria-label="전체 목차">${i("menu")}</button></nav></header>`;
const foot = `<footer class="ft"><b>${FOOT}</b>${LIC.map((l) => `<p>${l}</p>`).join("")}<p>고칠 곳과 질문: <a href="mailto:${D.CONTACT}">${D.CONTACT}</a></p></footer>`;
const crumb = (xs) => `<nav class="crumb" aria-label="현재 위치">${xs.map(([t, h], n) => (h ? `<a href="${h}">${t}</a>` : `<span>${t}</span>`) + (n < xs.length - 1 ? i("chevron-right") : "")).join("")}</nav>`;
const lecs = (nos) => (nos.length ? `<span class="lec">${nos.map((n) => `<a href="chapter.html" title="${esc(byNo[n].title)}">${n}</a>`).join("")}</span>` : `<span class="lec"><em>강의 준비 중</em></span>`);
const page = (title, cur, on, body, wide) => html(title, css, `${top(cur)}<div class="shell">${side(on)}<div><main class="main${wide ? " wide" : ""}">${body}</main>${foot}</div></div>`, kit);

/* 홈 */
const home = page(D.NAME, "", "home", `<div class="hs"><h1>AX 엔지니어 핸드북</h1><p class="desc">${esc(S.defn)}</p>
<button class="bigs" data-search>${i("search")}<span>무엇을 찾으세요? 예: 트랜잭션, MCP, 법인카드 정산</span><kbd>/</kbd></button>
<p class="hint">로드맵 주제, 강의 챕터, 명령어, 사례, 용어를 한 칸에서 찾아요. 어느 쪽에서든 <code>/</code>나 <code>Ctrl K</code>로 열려요.</p>
<div class="ix"><section class="ixb" id="start"><h2>${i("signpost")}나에게 맞는 시작점</h2><p>경험에 가까운 줄에서 시작해요</p><ul>${S.start.map((r, n) => `<li><a href="roadmap.html"><span class="n">${n + 1}</span>${esc(r.who)}</a></li>`).join("")}</ul></section>
<section class="ixb"><h2>${i("route")}로드맵 5단계</h2><p>원문 ax-engineer-roadmap ${S.version}</p><ul>${S.stages.map((s) => `<li><a href="roadmap.html"><span class="n">${s.no}</span>${esc(s.title)}<span class="c">${stageCount(s)}</span></a></li>`).join("")}</ul></section>
<section class="ixb"><h2>${i("book-open")}기초 강의</h2><p>${D.chapters.length}챕터, 배우는 순서대로</p><ul>${lecStages.map((s) => `<li><a href="chapter.html"><span class="n">${s.from}</span>${esc(s.title)}<span class="c">${s.list.length}챕터</span></a></li>`).join("")}</ul></section>
<section class="ixb"><h2>${i("layers")}사례와 자료</h2><p>바로 펴 보는 자료</p><ul>${LIB.map(([k, t, n]) => `<li><a href="cases.html">${t}<span class="c">${n}</span></a></li>`).join("")}</ul></section></div>
<section style="margin-top:40px" id="news"><h2 style="font-size:18px">최근 바뀐 것</h2><ul class="chg">${NEWS.map(([d, k, t]) => `<li><time>${d}</time><span class="badge ${k === "로드맵" ? "r" : ""}">${k}</span><span>${t}</span></li>`).join("")}</ul></section></div>`, true);

/* 로드맵 */
const roadmap = page("로드맵 · " + D.NAME, "roadmap", "roadmap", `<div>${crumb([["홈", "home.html"], ["로드맵"]])}<h1>AX 엔지니어 로드맵</h1><p class="desc">다섯 단계를 차례로 따라가요. 단계마다 읽을 문서, 다음 단계 전에 확인할 질문, 이어진 기초 강의가 있어요.</p>
<div class="metal"><span>${i("git-branch")}<span class="mono">ax-engineer-roadmap ${S.version}</span></span><span>${i("clock-3")}${S.commit.split("·")[1]} 기준</span><a href="${D.GH("README.md")}">${i("external-link")}원문 보기</a></div>
${S.stages.map((s) => `<section style="margin-top:40px"><h2 id="st${s.no}">${s.no}. ${esc(s.title)}</h2><p style="color:var(--sub);margin-top:6px;max-width:780px">${esc(s.lede)}</p>
<div class="tbl"><table><thead><tr><th style="width:44px">#</th><th>주제</th><th class="hide-m">다루는 것</th><th>이어진 강의</th></tr></thead><tbody>${stageTopics(s).map((t, n) => { const id = s.areas?.[n]?.id; const d = s.docs?.[n]?.d ?? s.areas?.[n]?.q ?? s.projects?.[n]?.out ?? (s.no === 5 ? S.cases[n].area : "핵심 질문, 주요 작업, 산출물, 통과 기준"); return `<tr><td class="n">${s.no}.${n + 1}</td><td><a href="topic.html">${esc(t)}</a></td><td class="hide-m"><small>${esc(d)}</small></td><td>${id ? lecs(AREA_LINKS[id]) : s.no === 4 && n === 0 ? lecs(["09", "10", "44"]) : s.no === 3 && n === 3 ? lecs(["32", "45", "46"]) : `<span class="lec"><em>—</em></span>`}</td></tr>`; }).join("")}</tbody></table></div>
${s.checks.length ? `<div class="call">${i("list-checks")}<div><h3>다음 단계로 가기 전에</h3>${s.checks.map((c) => `<p>${esc(c)}</p>`).join("")}</div></div>` : ""}</section>`).join("")}</div>
<aside class="otp"><h4>이 쪽의 내용</h4>${S.stages.map((s) => `<a href="#st${s.no}">${s.no}. ${esc(stageShort(s.title))}</a>`).join("")}</aside>`);

/* 로드맵 주제 */
const T = TOPIC;
const topic = page(T.title + " · 로드맵", "roadmap", "topic", `<article>${crumb([["로드맵", "roadmap.html"], ["2. " + stageShort(T.stage.title), "roadmap.html"], [T.title]])}<h1>${esc(T.title)}</h1><p class="desc">${esc(T.area.q)}</p>
<div class="metal"><span>${i("file-text")}<span class="mono">${T.src}</span></span><span>${i("git-branch")}${S.version}</span><a href="${D.GH(T.src)}">${i("pencil")}고치기 제안</a></div>
<div class="call">${i("book-open")}<div><h3>먼저 익힐 기초 강의</h3><p>이 문서를 읽기 전에 손에 익혀 두면 좋은 챕터예요.</p>
<div class="tbl"><table><tbody>${T.lec.map((n) => `<tr><td class="n">${n}</td><td><a href="chapter.html">${esc(byNo[n].title)}</a></td><td class="r"><small>${byNo[n].track} · ${byNo[n].level}</small></td></tr>`).join("")}</tbody></table></div></div></div>
<div class="prose"><h2 id="why">왜 필요한가</h2><p>${esc(T.why)}</p><h2 id="know">알아야 할 것</h2></div>
<div class="tbl"><table><thead><tr><th>항목</th><th style="width:150px">이어진 강의</th></tr></thead><tbody>${T.know.map((k) => `<tr><td>${esc(k.t)}</td><td>${lecs(k.lec)}</td></tr>`).join("")}</tbody></table></div>
<div class="prose">${T.body.o}</div>
<p class="edit">${i("pencil")}이 문서는 로드맵 레포에서 고쳐요. <a href="${D.GH(T.src)}">GitHub에서 고치기 제안</a></p>
<div class="pn"><a class="r" href="topic.html"><small>다음</small><b>${esc(T.next.t)}</b></a></div></article>
<aside class="otp"><h4>이 쪽의 내용</h4><a class="on" href="#why">왜 필요한가</a><a href="#know">알아야 할 것</a>${T.body.ids.map(([id, t]) => `<a href="#${id}">${esc(t)}</a>`).join("")}
<div class="blk"><h4>관련 자료</h4><a href="cases.html">${esc(S.cases[2].t)}</a><a href="cases.html">UI 통합 점검표</a></div></aside>`);

/* 강의 챕터 */
const c = CH.c;
const chapter = page(c.title + " · 강의", "lectures", "chapter", `<article>${crumb([["강의", "chapter.html"], [`${c.stage}. ${c.stageTitle}`, "chapter.html"], [`${c.no} ${short(c.title)}`]])}<h1>${c.no}. ${esc(c.title)}</h1><p class="desc">${esc(c.goal.replace(/`/g, ""))}</p>
<div class="metal"><span>${i("layers")}${c.track} · ${c.level}</span><span>${i("presentation")}슬라이드 ${CH.slides.length}쪽</span><span>${i("file-text")}<span class="mono">${c.dir}/README.md</span></span></div>
<div class="deck"><iframe src="${CH.deck}" title="${esc(c.title)} 슬라이드" loading="lazy"></iframe></div>
<div class="btns"><a href="${CH.deck}">${i("presentation")}크게 보기</a><a href="${CH.pdf}">${i("download")}PDF 받기</a></div>
<nav class="tabsx" aria-label="챕터 안내"><a aria-current="page" href="#">개요</a><a href="#">명령어 요약</a><a href="#">실습</a><a href="#">문제 해결</a></nav>
<div class="prose"><h2 id="g" style="border:0;margin-top:20px">배우는 것</h2><ul>${CH.goals.map((g) => `<li>${esc(g).replace(/`([^`]+)`/g, "<code>$1</code>")}</li>`).join("")}</ul><h2 id="p">구성</h2></div>
<div class="tbl"><table><thead><tr><th>파트</th><th class="r" style="width:96px">쪽</th></tr></thead><tbody>${CH.parts.map((p) => `<tr><td>${esc(p.p)}</td><td class="r"><small>${p.a}–${p.b}</small></td></tr>`).join("")}</tbody></table></div>
<div class="call">${i("route")}<div><h3>이 챕터를 쓰는 로드맵 주제</h3><p>${CH.used.map((u) => `<a style="color:var(--ac)" href="topic.html">${esc(u)}</a>`).join(", ")}에서 이 챕터를 기초로 써요.</p></div></div>
<div class="pn"><a href="chapter.html"><small>이전</small><b>${CH.prev.no} ${esc(short(CH.prev.title))}</b></a><a class="r" href="chapter.html"><small>다음</small><b>${CH.next.no} ${esc(short(CH.next.title))}</b></a></div></article>
<aside class="otp"><h4>슬라이드 파트</h4>${CH.parts.map((p, n) => `<a${n ? "" : ' class="on"'} href="#">${esc(p.p)}</a>`).join("")}<div class="blk"><h4>먼저 볼 챕터</h4><a href="chapter.html">${CH.prev.no} ${esc(short(CH.prev.title))}</a></div></aside>`);

/* 사례와 자료 */
const cases = page("사례와 자료 · " + D.NAME, "library", "cases", `<div>${crumb([["사례와 자료", "cases.html"], ["업무 사례"]])}<h1>업무 사례</h1><p class="desc">업무 하나를 원본 시스템, 승인 지점, 실패 대응까지 설계한 문서 ${S.cases.length}개예요. 실제 조직 성과가 아니라 공개 자료와 합성 데이터로 만든 설계예요.</p>
<div class="fl"><span class="sel">분야: 전체 ${i("chevron-down")}</span><span class="sel">산업: 전체 ${i("chevron-down")}</span><span class="sel">난이도: 전체 ${i("chevron-down")}</span><span class="sel">근거: 전체 ${i("chevron-down")}</span><span class="sel" style="margin-left:auto">추천 순서 ${i("chevron-down")}</span></div>
<div class="tbl" style="overflow-x:auto"><table><thead><tr><th style="width:36px">#</th><th>사례</th><th class="hide-m">분야 · 산업</th><th>난이도</th><th class="hide-m">위험</th><th class="hide-m">프로젝트</th><th class="hide-m">근거</th></tr></thead><tbody>
${S.cases.map((x, n) => `<tr><td class="n">${n + 1}</td><td><a href="cases.html">${esc(x.t)}</a></td><td class="hide-m"><small>${esc(x.area)} · ${esc(x.industry)}</small></td><td><span class="diff" title="난이도 ${x.diff}">${[1, 2, 3, 4, 5].map((k) => `<i class="${k <= x.diff ? "on" : ""}"></i>`).join("")}</span></td><td class="hide-m">${esc(x.risk)}</td><td class="hide-m mono" style="font-size:13px">${esc(x.p)}</td><td class="hide-m"><small>${esc(x.ev)}</small></td></tr>`).join("")}</tbody></table></div></div>`, true);

for (const [f, h] of Object.entries({ home, roadmap, topic, chapter, cases })) write("v12", f + ".html", h);
console.log("v12 ok");
