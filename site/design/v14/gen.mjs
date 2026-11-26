// 시안 v14 · 현장 수첩. 화면마다 질문이 먼저 서고, 할 일은 체크 칸으로 보여 줘요. 체크 표시는 저장하지 않아요.
import * as D from "../plan/data.mjs";
const { i, esc, S, byNo, short, stageShort, TOPIC, CH, LIB, NEWS, MENU, FOOT, LIC, html, DLG_CSS, kitFor, AREAS, stageTopics, stageCount, STAGE_LINKS, AREA_LINKS, SOON, HIRE_TOTAL, lecStages } = D;
import { write } from "../lib.mjs";

const css = `:root{--bg:#FFFEFB;--soft:#F5F3EC;--ink:#1D2330;--sub:#5D6474;--mute:#8E93A0;--line:#E6E2D8;--ac:#2459C9;--ac-s:#EDF2FC}
body{background:var(--bg);color:var(--ink);font-size:17px;line-height:1.6}.w{max-width:1080px;margin:0 auto;padding:0 28px}
.hd .w{display:flex;align-items:center;gap:24px;height:68px}.brand{display:flex;gap:10px;align-items:center;font-weight:800}.brand .mk{width:26px;height:26px;border:2px solid var(--ink);border-radius:6px;display:grid;place-items:center}.brand .mk svg{width:16px;height:16px;stroke-width:2.4}
.nav{display:flex;gap:6px;margin-left:12px}.nav a{padding:6px 12px;border-radius:999px;font-weight:600;font-size:16px;color:var(--sub)}.nav a:hover{background:var(--soft);color:var(--ink)}.nav a[aria-current]{background:var(--ink);color:#fff}
.hr{margin-left:auto;display:flex;gap:8px}.hr a,.hr button{height:40px;padding:0 16px;border-radius:999px;border:1.5px solid var(--ink);background:none;display:flex;align-items:center;gap:8px;font-weight:700;font-size:15px;cursor:pointer}.hr a{background:var(--ac);border-color:var(--ac);color:#fff}
.hd{border-bottom:1.5px solid var(--ink)}
.lab{display:inline-flex;align-items:center;gap:8px;font-family:"JetBrains Mono","D2Coding Hangul",monospace;font-size:13px;color:var(--sub)}
h1{font-size:48px;line-height:1.2;font-weight:800;letter-spacing:-.03em}h2{font-size:30px;line-height:1.3;font-weight:800;letter-spacing:-.02em}h3{font-size:19px;font-weight:700;line-height:1.4}
main{padding:52px 0 88px}.sec{margin-top:80px}.sub{color:var(--sub);margin-top:8px;max-width:640px}
/* 질문 고르기 */
.ask{margin-top:28px;display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:24px;align-items:start}
.opts{display:flex;flex-direction:column;gap:8px}.opt{display:flex;gap:14px;align-items:center;width:100%;text-align:left;padding:14px 16px;border:1.5px solid var(--line);border-radius:12px;background:#fff;cursor:pointer;font-size:16px;font-weight:600}
.opt:hover{border-color:var(--ink)}.opt i{width:20px;height:20px;border-radius:50%;border:2px solid var(--mute);flex:none;display:block}.opt[aria-pressed=true]{border-color:var(--ink);box-shadow:3px 3px 0 var(--ink)}.opt[aria-pressed=true] i{border:6px solid var(--ac)}
.plan{border:1.5px solid var(--ink);border-radius:14px;background:#fff;padding:24px 26px;position:sticky;top:20px}.plan h3{font-size:22px}.plan .first{margin-top:6px;color:var(--sub);font-size:15px}
.todo{list-style:none;padding:0;margin:18px 0 0}.todo li{display:grid;grid-template-columns:26px minmax(0,1fr);gap:12px;padding:12px 0;border-top:1px dashed var(--line)}.todo li:first-child{border-top:0}
.cb{width:22px;height:22px;border:2px solid var(--ink);border-radius:5px;background:#fff;display:grid;place-items:center;cursor:pointer;padding:0;margin-top:2px}.cb svg{width:15px;height:15px;stroke-width:3;opacity:0;color:#fff}.cb[aria-checked=true]{background:var(--ink)}.cb[aria-checked=true] svg{opacity:1}
.todo b{display:block;font-size:16px}.todo small{display:block;color:var(--sub);font-size:14px;margin-top:2px}.todo a{color:var(--ac);text-decoration:underline;text-underline-offset:3px}
.save{font-size:13px;color:var(--mute);margin-top:12px;display:flex;gap:6px;align-items:center}.save svg{width:14px;height:14px}
/* 단계 질문 */
.qs{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin-top:24px}.qc{border:1.5px solid var(--line);border-radius:14px;padding:18px;background:#fff;display:flex;flex-direction:column;gap:10px}.qc:hover{border-color:var(--ink)}
.qc .n{font-family:"JetBrains Mono",monospace;font-size:13px;color:var(--sub)}.qc b{font-size:17px;line-height:1.4}.qc p{font-size:14px;color:var(--sub)}.qc .q{margin-top:auto;padding-top:12px;border-top:1px dashed var(--line);font-size:14px}
.row3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.pan{border:1.5px solid var(--line);border-radius:14px;padding:20px 22px;background:#fff}.pan h3{font-size:17px}.pan p{font-size:14px;color:var(--sub)}
.big{font-size:44px;font-weight:800;letter-spacing:-.02em;line-height:1;margin:12px 0 6px}.big small{font-size:18px;margin-left:3px}
.ul{list-style:none;padding:0;margin:10px 0 0}.ul li{display:flex;gap:10px;padding:7px 0;border-top:1px dashed var(--line);font-size:15px}.ul li:first-child{border:0}.ul time{color:var(--mute);font-size:13px;font-family:"JetBrains Mono",monospace;flex:none;padding-top:2px}.ul a:hover{color:var(--ac)}.ul .c{margin-left:auto;color:var(--sub)}
.ft{border-top:1.5px solid var(--ink);padding:28px 0 44px;font-size:14px;color:var(--sub)}.ft b{color:var(--ink)}.ft p{margin-top:4px}.ft a{text-decoration:underline}
/* 로드맵 */
.stage{display:grid;grid-template-columns:minmax(0,4fr) minmax(0,7fr);gap:40px;padding:40px 0;border-top:1.5px solid var(--ink)}.stage:first-of-type{margin-top:36px}
.stage .num{font-family:"JetBrains Mono",monospace;font-size:14px;color:var(--sub)}.stage h2{margin-top:6px}.stage .lede{color:var(--sub);margin-top:10px;font-size:15px}
.box{background:var(--soft);border-radius:14px;padding:18px 20px}.box h3{font-size:15px;display:flex;gap:8px;align-items:center}.box h3 svg{width:16px;height:16px}
.reads{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:14px}.reads a{display:flex;gap:10px;align-items:baseline;padding:10px 12px;border:1.5px solid var(--line);border-radius:10px;background:#fff;font-size:15px}.reads a:hover{border-color:var(--ink)}
.reads small{margin-left:auto;font-size:12px;color:var(--sub);white-space:nowrap}.reads .k{font-family:"JetBrains Mono",monospace;font-size:12px;color:var(--mute)}
/* 주제와 챕터 */
.hero{padding-bottom:36px;border-bottom:1.5px solid var(--ink)}.hero .qq{font-size:40px;line-height:1.3;font-weight:800;letter-spacing:-.025em;margin-top:14px;max-width:880px}.hero .tt{font-size:18px;color:var(--sub);margin-top:14px}
.step{display:grid;grid-template-columns:64px minmax(0,1fr);gap:20px;padding:40px 0;border-bottom:1px dashed var(--line)}.step .sn{width:48px;height:48px;border:1.5px solid var(--ink);border-radius:50%;display:grid;place-items:center;font-weight:800;font-size:18px}
.step h2{font-size:26px}.step .sub{margin-top:4px}
.chips{display:flex;flex-wrap:wrap;gap:6px}.chips a{font-size:13px;padding:2px 10px;border-radius:999px;border:1.5px solid var(--ink);font-weight:600}.chips a:hover{background:var(--ink);color:#fff}.chips em{font-style:normal;font-size:13px;color:var(--mute);padding:3px 0}
.todo.wide li{grid-template-columns:26px minmax(0,1fr) auto;align-items:start}
.prose{max-width:760px}.prose h2{font-size:24px;margin:44px 0 12px}.prose h3{margin:26px 0 8px;font-size:18px}.prose p{margin:12px 0}.prose ul,.prose ol{padding-left:22px}.prose li{margin:5px 0}.prose a{color:var(--ac);text-decoration:underline}
code{font-family:"JetBrains Mono","D2Coding Hangul",monospace;font-size:.86em;background:var(--soft);padding:1px 5px;border-radius:4px}.tw{overflow-x:auto;margin:16px 0;border:1.5px solid var(--line);border-radius:12px;background:#fff}
.tw table{border-collapse:collapse;width:100%;font-size:15px}.tw th,.tw td{text-align:left;vertical-align:top;padding:10px 14px;border-bottom:1px solid var(--line)}.tw tr:last-child td{border:0}.tw th{background:var(--soft)}
.nx{display:flex;justify-content:space-between;gap:16px;margin-top:48px}.nx a{flex:1;max-width:420px;border:1.5px solid var(--ink);border-radius:14px;padding:16px 20px}.nx a:hover{box-shadow:3px 3px 0 var(--ink)}.nx small{display:flex;gap:6px;align-items:center;color:var(--sub);font-size:14px}.nx b{font-size:18px}.nx .r{text-align:right;margin-left:auto}.nx .r small{justify-content:flex-end}
.deck{position:relative;aspect-ratio:16/9;border-radius:14px;overflow:hidden;border:1.5px solid var(--ink);background:#111}.deck iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.acts{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}.acts a{height:40px;padding:0 16px;border-radius:999px;border:1.5px solid var(--ink);display:flex;align-items:center;gap:8px;font-weight:700;font-size:15px}.acts a:hover{background:var(--ink);color:#fff}.acts svg{width:17px;height:17px}
/* 사례 */
.areas{display:flex;flex-wrap:wrap;gap:8px;margin-top:22px}.areas button{height:44px;padding:0 18px;border-radius:999px;border:1.5px solid var(--line);background:#fff;font-size:16px;font-weight:600;cursor:pointer}.areas button[aria-pressed=true]{border-color:var(--ink);background:var(--ink);color:#fff}
.lnk{display:flex;gap:8px;flex-wrap:wrap;margin-top:28px;font-size:15px}.lnk a{padding:6px 12px;border-radius:8px;background:var(--soft)}.lnk a[aria-current]{background:var(--ac-s);color:var(--ac);font-weight:700}.lnk a b{margin-left:4px;font-weight:500;color:var(--sub)}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:24px}.card{border:1.5px solid var(--line);border-radius:14px;background:#fff;padding:20px 22px}.card:hover{border-color:var(--ink)}
.card .top{display:flex;justify-content:space-between;gap:10px;font-size:13px;color:var(--sub)}.card h3{margin-top:6px;font-size:18px}.card dl{margin:14px 0 0;display:grid;grid-template-columns:auto minmax(0,1fr);gap:6px 14px;font-size:14.5px}.card dt{color:var(--sub)}.card dd{margin:0}
.dots{display:inline-flex;gap:3px;align-items:center}.dots i{width:8px;height:8px;border-radius:50%;background:var(--line);display:block}.dots i.on{background:var(--ink)}
${DLG_CSS({ scrim: "rgba(29,35,48,.45)", bg: "#fff", ink: "#1D2330", line: "#E6E2D8", sub: "#5D6474", r: "14px", hover: "#F5F3EC" })}
@media (max-width:980px){.qs{grid-template-columns:repeat(2,minmax(0,1fr))}.ask{grid-template-columns:1fr}.plan{position:static}.nav{display:none}.stage{grid-template-columns:1fr;gap:20px}}
@media (max-width:680px){.w{padding:0 16px}h1{font-size:34px}h2{font-size:24px}.hero .qq{font-size:28px}.qs,.row3,.cards,.reads{grid-template-columns:1fr}.step{grid-template-columns:1fr;gap:12px}.hr button span{display:none}.hr button{padding:0 11px}
.todo.wide li{grid-template-columns:26px minmax(0,1fr)}.todo.wide li .chips{grid-column:2}.nx{flex-direction:column}.nx a{max-width:none}}`;

const kitB = kitFor();
const js = `<script>document.querySelectorAll('.cb').forEach(b=>b.onclick=()=>b.setAttribute('aria-checked',b.getAttribute('aria-checked')!=='true'));
document.querySelectorAll('[data-opt]').forEach(o=>o.onclick=()=>{document.querySelectorAll('[data-opt]').forEach(x=>x.setAttribute('aria-pressed',x===o));document.querySelectorAll('[data-plan]').forEach(p=>p.hidden=p.dataset.plan!==o.dataset.opt)});
document.querySelectorAll('.areas button').forEach(o=>o.onclick=()=>{document.querySelectorAll('.areas button').forEach(x=>x.setAttribute('aria-pressed',x===o));const a=o.dataset.a;document.querySelectorAll('.card').forEach(c=>c.hidden=a!=='all'&&c.dataset.a!==a)});</script>`;
const kit = { dlg: kitB.dlg, js: kitB.js + js };
const head = (cur) => `<header class="hd"><div class="w"><a class="brand" href="home.html"><span class="mk">${i("check")}</span>${D.NAME}</a>
<nav class="nav" aria-label="메뉴">${MENU.map(([k, t, h]) => `<a href="${h}"${k === cur ? ' aria-current="page"' : ""}>${t}</a>`).join("")}</nav>
<div class="hr"><button data-search>${i("search")}<span>찾기</span></button><a href="home.html#start">시작하기</a></div></div></header>`;
const foot = `<footer class="ft"><div class="w"><b>${FOOT}</b>${LIC.map((l) => `<p>${l}</p>`).join("")}<p>고칠 곳과 질문: <a href="mailto:${D.CONTACT}">${D.CONTACT}</a></p></div></footer>`;
const cb = (on) => `<button class="cb" role="checkbox" aria-checked="${on ? "true" : "false"}" aria-label="했어요">${i("check")}</button>`;
const save = `<p class="save">${i("info")}체크 표시는 이 화면에서만 쓰고 저장하지 않아요.</p>`;
const chips = (nos) => (nos.length ? `<span class="chips">${nos.map((n) => `<a href="chapter.html" title="${esc(byNo[n].title)}">${n} ${esc(short(byNo[n].title))}</a>`).join("")}</span>` : `<span class="chips"><em>강의 준비 중</em></span>`);

/* 홈: 질문 고르기 */
const PLANS = [
  [["경험별 진입 경로 1 읽기", "개발이 처음인 사람을 위한 순서예요"], ["로드맵 2단계 <a href='topic.html'>소프트웨어와 API</a>", "알아야 할 것 8줄을 읽어요"], ["기초 강의 01부터 차례로", "터미널, Git, 파이썬, SQL 순서예요"], ["4단계 P1 안전한 보조 도구", "첫 결과물을 만들어요"]],
  [["경험별 진입 경로 2 읽기", "아는 것은 건너뛰고 빈 곳만 채워요"], ["로드맵 3단계 업무 전환 8단계", "목표와 경계부터 표준화까지"], ["업무 사례 하나 고르기", "P1~P3을 그 사례로 연습해요"], ["채용 현황에서 공고 해설 읽기", "공고가 요구하는 것과 비교해요"]],
  [["경험별 진입 경로 3 읽기", "현업 실무자 협업 안내예요"], ["용어 사전 20개", "API, RAG, MCP가 업무에서 뜻하는 것"], ["업무 전환 1~2단계", "목표와 경계, 현재 업무 파악"], ["템플릿 업무 발굴 카드 복사", "우리 팀 업무 하나를 적어 봐요"]],
  [["용어 사전 20개", "용어마다 업무에서 꼭 물을 질문이 있어요"], ["로드맵 1단계 직무 이해하기", "AX 엔지니어가 하는 일과 하지 않는 일"], ["공개 AX 사례 둘러보기", "우리 산업과 가까운 사례부터"]],
  [["합성 VOC 실행 안내", "외부 계정이나 API 없이 돌려요"], ["결과 대시보드 보기", "합성 데이터 16건으로 만든 결과예요"], ["업무 사례 Beauty/D2C VOC", "같은 예제를 설계 문서로 읽어요"]],
  [["강의 챕터 열기", "오늘 배운 챕터의 슬라이드를 다시 봐요"], ["PDF 받기", "슬라이드 아래 버튼으로 받아요"], ["이 챕터를 쓰는 로드맵 주제", "배운 것을 어디에 쓰는지 봐요"]],
];
const WHO = [...S.start.map((r) => [r.who, r.first]), ["지금 수업을 듣고 있다", "오늘 배운 챕터 다시 보기"]];
const home = html(D.NAME, css, `${head("")}<main><div class="w">
<span class="lab">${i("route")}AX 엔지니어 공개 로드맵 ${S.version}</span><h1 style="margin-top:14px">어떤 질문을 갖고 오셨나요?</h1><p class="sub" style="font-size:18px">${esc(S.defn)}</p>
<div class="ask" id="start"><div class="opts" role="group" aria-label="내 질문">${WHO.map(([w], n) => `<button class="opt" data-opt="${n}" aria-pressed="${n === 0}"><i></i>${esc(w)}</button>`).join("")}</div>
<div>${WHO.map(([w, f], n) => `<section class="plan" data-plan="${n}"${n ? " hidden" : ""}><span class="lab">이렇게 해 봐요</span><h3 style="margin-top:6px">${esc(w)}</h3><p class="first">첫 결과물: ${esc(f)}</p>
<ol class="todo">${PLANS[n].map(([t, s]) => `<li>${cb(false)}<div><b>${t}</b><small>${s}</small></div></li>`).join("")}</ol>${save}</section>`).join("")}</div></div>
<section class="sec"><h2>단계마다 스스로 묻는 질문</h2><p class="sub">로드맵 5단계예요. 아래 질문에 답할 수 있으면 다음 단계로 가요.</p>
<div class="qs">${S.stages.map((s) => `<a class="qc" href="roadmap.html"><span class="n">${s.no}단계 · ${stageCount(s)}</span><b>${esc(s.title)}</b><p>${esc(D.firstSentence(s.lede))}</p><span class="q">${s.checks[0] ? esc(s.checks[0].replace(/\.$/, "")) + "?" : s.projects ? "남길 것: " + esc(s.projects[0].out) : "할 일: 추천 순서대로 사례 하나 고르기"}</span></a>`).join("")}</div></section>
<section class="sec row3" id="news"><div class="pan"><h3>이번 달 채용 공고</h3><div class="big">${HIRE_TOTAL}<small>건</small></div><p>2026년 10월 국내 ${S.hiring.rows.map((r) => `${r.type} ${r.n}`).join(", ")}. ${esc(S.hiring.note)}</p></div>
<div class="pan"><h3>사례와 자료</h3><ul class="ul">${LIB.slice(0, 4).map(([k, t, n]) => `<li><a href="cases.html">${t}</a><span class="c">${n}</span></li>`).join("")}</ul></div>
<div class="pan"><h3>소식</h3><ul class="ul">${NEWS.slice(0, 3).map(([d, k, t]) => `<li><time>${d.slice(5)}</time><span>${t}</span></li>`).join("")}</ul></div></section>
</div></main>${foot}`, kit);

/* 로드맵 */
const roadmap = html("로드맵 · " + D.NAME, css, `${head("roadmap")}<main><div class="w">
<span class="lab">${i("route")}로드맵 ${S.version} · 원문 ax-engineer-roadmap</span><h1 style="margin-top:14px">단계마다 질문에 답하며 가요</h1><p class="sub" style="font-size:18px">왼쪽 질문에 답할 수 있으면 다음 단계로 가요. 오른쪽은 그 답을 찾을 때 읽을 것과 먼저 익힐 기초 강의예요.</p>
${S.stages.map((s) => `<section class="stage"><div><span class="num">${s.no}단계 · ${stageCount(s)}</span><h2>${esc(s.title)}</h2><p class="lede">${esc(s.lede)}</p>
<div class="box" style="margin-top:20px"><h3>${i("list-checks")}${s.checks.length ? "이 단계를 마치면" : s.projects ? "프로젝트마다 남길 것" : "이 단계에서 할 일"}</h3><ol class="todo">${(s.checks.length ? s.checks : s.projects ? s.projects.map((p) => `${p.t.split(" · ")[0]}: ${p.out}`) : ["업무 사례 15개 가운데 추천 순서대로 하나를 고른다.", "원본 시스템, 승인 지점, 실패 대응을 내 업무와 비교한다."]).map((c) => `<li>${cb(false)}<div><small style="color:var(--ink);font-size:15px">${esc(c)}</small></div></li>`).join("")}</ol></div></div>
<div><h3 style="font-size:15px;color:var(--sub)">읽을 것</h3><div class="reads">${stageTopics(s).map((t, n) => { const id = s.areas?.[n]?.id; const ls = id ? AREA_LINKS[id] : []; return `<a href="topic.html"><span class="k">${s.no}.${n + 1}</span><span>${esc(t)}</span>${ls.length ? `<small>강의 ${ls.length}</small>` : id ? `<small>준비 중</small>` : ""}</a>`; }).join("")}</div>
${STAGE_LINKS[s.no].length && s.no !== 2 ? `<h3 style="font-size:15px;color:var(--sub);margin-top:20px">먼저 익힐 기초 강의</h3><div style="margin-top:8px">${chips(STAGE_LINKS[s.no])}</div>` : ""}</div></section>`).join("")}
</div></main>${foot}`, kit);

/* 로드맵 주제 */
const T = TOPIC;
const topic = html(T.title + " · 로드맵", css, `${head("roadmap")}<main><div class="w">
<section class="hero"><span class="lab"><a href="roadmap.html">로드맵</a> / 2단계 ${esc(stageShort(T.stage.title))} / ${esc(T.title)}</span><p class="qq">${esc(T.area.q)}</p><p class="tt">이 질문에 답하는 주제가 <b style="color:var(--ink)">${esc(T.title)}</b>이에요. ${esc(T.why.split(". ")[0])}.</p></section>
<section class="step"><span class="sn">1</span><div><h2>먼저 손에 익히기</h2><p class="sub">문서를 읽기 전에 따라 해 볼 기초 강의예요. 01부터 차례로 들어도 돼요.</p>
<ol class="todo wide">${T.lec.map((n) => `<li>${cb(false)}<div><b><a href="chapter.html">${n} ${esc(byNo[n].title)}</a></b><small>${byNo[n].track} · ${byNo[n].level}</small></div></li>`).join("")}</ol></div></section>
<section class="step"><span class="sn">2</span><div><h2>알아야 할 것</h2><p class="sub">줄마다 설명할 수 있으면 체크해요. 오른쪽은 그 줄에 이어진 강의예요.</p>
<ol class="todo wide">${T.know.map((k) => `<li>${cb(false)}<div><b style="font-weight:600">${esc(k.t)}</b></div>${chips(k.lec)}</li>`).join("")}</ol>${save}</div></section>
<section class="step"><span class="sn">3</span><div><h2>문서 읽기</h2><p class="sub">로드맵 레포의 문서를 그대로 옮겼어요. <a style="color:var(--ac);text-decoration:underline" href="${D.GH(T.src)}">원문과 고치기 제안</a></p><div class="prose">${T.body.o}</div></div></section>
<nav class="nx" aria-label="주제 이동"><a href="roadmap.html"><small>${i("arrow-left")}2단계 목록</small><b>${esc(T.stage.title)}</b></a><a class="r" href="topic.html"><small>다음 질문 ${i("arrow-right")}</small><b>${esc(T.next.q)}</b></a></nav>
</div></main>${foot}`, kit);

/* 강의 챕터 */
const c = CH.c;
const chapter = html(c.title + " · 강의", css, `${head("lectures")}<main><div class="w">
<section class="hero"><span class="lab"><a href="chapter.html">강의</a> / ${c.stage}단계 ${esc(c.stageTitle)} / ${c.no}</span><h1 style="margin-top:12px">${esc(c.title)}</h1><p class="tt">${esc(c.goal.replace(/`/g, ""))}</p></section>
<section class="step"><span class="sn">1</span><div><h2>이 챕터를 마치면 할 수 있어요</h2><ol class="todo">${CH.goals.map((g) => `<li>${cb(false)}<div><b style="font-weight:600">${esc(g).replace(/`([^`]+)`/g, "<code>$1</code>")}</b></div></li>`).join("")}</ol>${save}</div></section>
<section class="step"><span class="sn">2</span><div><h2>슬라이드로 배우기</h2><p class="sub">${CH.slides.length}쪽, 파트 ${CH.parts.length}개예요. 방향키로 넘기고 아래 막대에서 PDF를 받아요.</p>
<div class="deck" style="margin-top:18px"><iframe src="${CH.deck}" title="${esc(c.title)} 슬라이드" loading="lazy"></iframe></div><div class="acts"><a href="${CH.deck}">${i("presentation")}크게 보기</a><a href="${CH.pdf}">${i("download")}PDF 받기</a></div>
<ol class="todo" style="margin-top:20px">${CH.parts.map((p) => `<li>${cb(false)}<div><b style="font-weight:600">${esc(p.p)}</b><small>${p.a}–${p.b}쪽</small></div></li>`).join("")}</ol></div></section>
<section class="step"><span class="sn">3</span><div><h2>어디에 쓰나요</h2><p class="sub">이 챕터를 기초로 쓰는 로드맵 주제예요.</p><div class="reads" style="max-width:560px">${CH.used.map((u) => `<a href="topic.html"><span class="k">2.1</span><span>${esc(u)}</span><small>${esc(TOPIC.area.q.slice(0, 18))}…</small></a>`).join("")}</div></div></section>
<nav class="nx" aria-label="챕터 이동"><a href="chapter.html"><small>${i("arrow-left")}이전 챕터</small><b>${CH.prev.no} ${esc(short(CH.prev.title))}</b></a><a class="r" href="chapter.html"><small>다음 챕터 ${i("arrow-right")}</small><b>${CH.next.no} ${esc(short(CH.next.title))}</b></a></nav>
</div></main>${foot}`, kit);

/* 사례와 자료 */
const cases = html("사례와 자료 · " + D.NAME, css, `${head("library")}<main><div class="w">
<span class="lab">${i("layers")}사례와 자료 / 업무 사례</span><h1 style="margin-top:14px">어떤 업무를 바꾸려고 하나요?</h1><p class="sub" style="font-size:18px">업무 분야를 고르면 비슷한 설계 사례가 나와요. 사례마다 무엇을 자동으로 하고 어디서 사람이 판단하는지 적혀 있어요.</p>
<div class="areas" role="group" aria-label="업무 분야"><button aria-pressed="true" data-a="all">전체 ${S.cases.length}</button>${AREAS.map((a) => `<button aria-pressed="false" data-a="${esc(a)}">${esc(a)}</button>`).join("")}</div>
<div class="cards">${S.cases.map((x) => `<a class="card" href="cases.html" data-a="${esc(x.area)}"><div class="top"><span>${esc(x.area)} · ${esc(x.industry)}</span><span class="dots" title="난이도 ${x.diff}">${[1, 2, 3, 4, 5].map((k) => `<i class="${k <= x.diff ? "on" : ""}"></i>`).join("")}</span></div><h3>${esc(x.t)}</h3>
<dl><dt>쓰기 범위</dt><dd>${esc(x.scope)}</dd><dt>위험</dt><dd>${esc(x.risk)}</dd><dt>연습</dt><dd>${esc(x.p)}</dd><dt>근거</dt><dd>${esc(x.ev)}</dd></dl></a>`).join("")}</div>
<nav class="lnk" aria-label="다른 자료">${LIB.map(([k, t, n]) => `<a href="cases.html"${k === "cases" ? ' aria-current="page"' : ""}>${t}<b>${n}</b></a>`).join("")}</nav>
</div></main>${foot}`, kit);

for (const [f, h] of Object.entries({ home, roadmap, topic, chapter, cases })) write("v14", f + ".html", h);
console.log("v14 ok");
