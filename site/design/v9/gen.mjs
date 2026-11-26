// 시안 v9 · 사이트 하나, 레포 둘. 로드맵(ax-engineer-roadmap)과 강의(이 레포의 덱)를 빌드할 때 같이 읽어요.
// 메뉴: 로드맵 · 강의 · 사례와 자료 · 소식. 로드맵 주제마다 "먼저 익힐 기초"로 강의 챕터를 이어요.
import fs from "node:fs";
import path from "node:path";
import { i, esc, write, chapters, byNo, stages as courseStages, cur } from "../lib.mjs";
import { searchKit, DLG_CSS, html, deck, pdf, md } from "../new/content.mjs";

const S = JSON.parse(fs.readFileSync(path.join(import.meta.dirname, "snapshot.json"), "utf8"));
const GH = (p) => `https://github.com/woogi-kang/ax-engineer-roadmap/blob/main/${p}`;
const COPY = "© 2026 Taewook Kang (woogi) · woogi@memoriz.net";

/* 로드맵 주제와 강의 챕터 잇기(초안). 실제로는 강의 레포에 links 파일 하나로 두고 빌드할 때 양쪽에 붙여요 */
const AREA_LINKS = {
  "software-and-api": ["01", "02", "12", "19", "28", "31", "36", "44"],
  "llm-foundations": ["12", "13", "15"],
  "agent-systems": ["19", "21", "24"],
  "tools-and-mcp": ["11", "19", "44"],
  "evaluation-and-testing": ["39", "45", "46"],
  "production-operations": ["29", "30", "31", "35"],
  "security-and-privacy": ["33", "37", "43", "44"],
};
const STAGE_LINKS = { 1: [], 2: null, 3: ["32", "45", "46"], 4: ["09", "10", "44"], 5: ["45"] };
const ITEM_LINKS = [["31"], ["33", "34"], [], ["32", "36", "37", "43"], ["37"], [], ["29", "30", "33"], ["28"]];
const SOON = { "llm-foundations": "LLM 강의 준비 중", "agent-systems": "에이전트 강의 준비 중", "tools-and-mcp": "MCP 강의 준비 중", "evaluation-and-testing": "평가 강의 준비 중" };
const usedBy = {};
for (const [a, nos] of Object.entries(AREA_LINKS)) for (const n of nos) (usedBy[n] ??= []).push(S.stages[1].areas.find((x) => x.id === a).t);
for (const [st, nos] of Object.entries(STAGE_LINKS)) for (const n of nos || []) (usedBy[n] ??= []).push(`${st}단계 ${S.stages[st - 1].title}`);

const css = `:root{--bg:#FFFFFF;--paper:#F6F5F1;--ink:#16181D;--sub:#5B6070;--mute:#8A8F9C;--line:#E2E0D9;--line2:#CFCCC2;--ac:#2459C9;--ac-s:#EAF0FC;--lec:#1F8A4C;--lec-s:#E7F4EC;--warn:#B26A00}
[data-theme=dark]{--bg:#121418;--paper:#181B21;--ink:#ECEDEF;--sub:#A3A8B3;--mute:#7C818D;--line:#2B2F38;--line2:#3A3F4A;--ac:#86A8F2;--ac-s:#1D2740;--lec:#5CC08A;--lec-s:#16271D;--warn:#E3A64A}
body{background:var(--bg);color:var(--ink);font-size:16px;line-height:1.65}
.wrap{max-width:1200px;margin:0 auto;padding:0 24px}
.hd{border-bottom:1px solid var(--line);background:var(--bg);position:sticky;top:0;z-index:10}.hd .wrap{display:flex;align-items:center;gap:28px;height:60px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;white-space:nowrap}.bm{width:28px;height:28px;border-radius:7px;background:var(--ink);color:var(--bg);display:grid;place-items:center}.bm .i{width:16px;height:16px}
.nav{display:flex;gap:2px}.nav a{padding:6px 11px;border-radius:6px;color:var(--sub);font-weight:600;font-size:15px;white-space:nowrap}.nav a[aria-current]{color:var(--ink);background:var(--paper)}
.tools{margin-left:auto;display:flex;gap:8px}.sbtn{display:flex;align-items:center;gap:8px;height:36px;padding:0 10px 0 12px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--sub);cursor:pointer;font-size:14px;min-width:210px}.sbtn kbd{margin-left:auto;font-size:12px;border:1px solid var(--line);border-radius:5px;padding:0 6px}
.ibtn{width:36px;height:36px;display:grid;place-items:center;border:1px solid var(--line);border-radius:8px;background:var(--bg);cursor:pointer}[data-theme=light] .moon-i{}[data-theme=light] .ibtn .moon-i,[data-theme=dark] .ibtn .sun-i{display:none}
h1,h2,h3{letter-spacing:-.02em}
.btn{display:inline-flex;align-items:center;gap:8px;height:44px;padding:0 18px;border-radius:9px;font-weight:700;border:1.5px solid var(--ink);white-space:nowrap}.btn.pri{background:var(--ink);color:var(--bg)}.btns{display:flex;gap:10px;flex-wrap:wrap}
.lbl{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:700;padding:2px 8px;border-radius:5px;white-space:nowrap}.lbl.rm{background:var(--ac-s);color:var(--ac)}.lbl.lc{background:var(--lec-s);color:var(--lec)}.lbl .i{width:14px;height:14px}
.chip{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:600;padding:3px 9px;border-radius:99px;border:1px solid var(--line);white-space:nowrap;background:var(--bg)}.chip b{color:var(--lec)}.chip.soon{color:var(--mute);border-style:dashed}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.sec{padding:56px 0;border-top:1px solid var(--line)}.sec-h{display:flex;justify-content:space-between;align-items:end;gap:16px;margin-bottom:22px;flex-wrap:wrap}.sec-h h2{font-size:28px}.sec-h p{color:var(--sub);margin-top:4px}.more{display:inline-flex;gap:4px;align-items:center;color:var(--ac);font-weight:700;font-size:15px}.more .i{width:16px;height:16px}
.ft{border-top:1px solid var(--line);padding:32px 0 44px;color:var(--sub);font-size:14px}.ft .wrap{display:grid;grid-template-columns:1fr 1fr;gap:20px}.ft b{color:var(--ink);display:block;margin-bottom:4px}.ft p+p{margin-top:2px}
/* 홈 */
.hero{padding:60px 0 44px}.hero .wrap{display:grid;grid-template-columns:minmax(0,1fr) 440px;gap:56px;align-items:center}
.hero h1{font-size:46px;line-height:1.22;font-weight:800}.hero .def{margin-top:18px;color:var(--sub);font-size:18px;max-width:620px}.hero .btns{margin-top:26px}
.two{border:1px solid var(--line);border-radius:16px;padding:22px;background:var(--paper)}
.two h3{font-size:14px;color:var(--sub);font-weight:600}
.row{display:flex;gap:6px;margin-top:10px}.row span{flex:1;min-width:0;text-align:center;font-size:13px;font-weight:700;padding:8px 2px;border-radius:8px;line-height:1.3}
.row.rm span{background:var(--bg);border:1.5px solid var(--ac);color:var(--ac)}.row.rm span.on{background:var(--ac);color:#fff}
.row.lc span{background:var(--bg);border:1.5px solid var(--lec);color:var(--lec)}
.wire{height:34px;position:relative;margin:0 0}.wire svg{width:100%;height:100%}
.two p{font-size:14px;color:var(--sub);margin-top:14px;line-height:1.55}
.start{width:100%;border-collapse:collapse}.start td{padding:14px 16px 14px 0;border-bottom:1px solid var(--line);vertical-align:top}.start tr:first-child td{border-top:1px solid var(--line)}
.start td:first-child{font-weight:700;width:34%}.start td:nth-child(2){color:var(--ac);font-weight:600;width:30%}.start td:last-child{color:var(--sub)}
.stg{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;counter-reset:s}
.stc{position:relative;border:1.5px solid var(--line2);border-radius:14px;padding:18px 16px 16px;display:flex;flex-direction:column;background:var(--bg)}.stc:hover{border-color:var(--ac)}
.stc .n{width:30px;height:30px;border-radius:50%;background:var(--ink);color:var(--bg);display:grid;place-items:center;font-weight:800;font-size:14px}
.stc h3{font-size:18px;margin-top:12px;line-height:1.35}.stc .c{color:var(--ac);font-weight:700;font-size:14px;margin-top:2px}.stc p{color:var(--sub);font-size:14px;margin-top:8px;line-height:1.5;flex:1}
.stc .lk{margin-top:14px;padding-top:12px;border-top:1px dashed var(--line);font-size:13px;color:var(--lec);font-weight:700;display:flex;gap:6px;align-items:center}.stc .lk.none{color:var(--mute);font-weight:500}.stc .lk .i{width:15px;height:15px}
.grid2{display:grid;grid-template-columns:1.4fr 1fr;gap:28px}
.case{display:grid;grid-template-columns:auto minmax(0,1fr);gap:4px 14px;padding:16px 0;border-bottom:1px solid var(--line)}.case:first-of-type{border-top:1px solid var(--line)}
.dots{display:flex;gap:3px;padding-top:7px}.dots i{width:8px;height:8px;border-radius:50%;background:var(--line2)}.dots i.on{background:var(--ink)}
.case b{line-height:1.4}.case small{grid-column:2;color:var(--sub);font-size:14px}
.hire{border:1px solid var(--line);border-radius:14px;padding:20px}.hire h3{font-size:17px}.hire .big{font-size:40px;font-weight:800;letter-spacing:-.03em;margin-top:6px}.hire .big small{font-size:16px;font-weight:600;color:var(--sub);margin-left:6px}
.bars{margin-top:12px;display:flex;flex-direction:column;gap:8px}.bar{display:grid;grid-template-columns:76px minmax(0,1fr) 34px;gap:10px;align-items:center;font-size:14px}.bar i{display:block;height:10px;border-radius:5px;background:var(--ac)}.bar em{font-style:normal;text-align:right;font-weight:700}
.hire p{font-size:13px;color:var(--mute);margin-top:12px;line-height:1.5}
.news{list-style:none;margin:0;padding:0}.news li{display:grid;grid-template-columns:100px auto minmax(0,1fr);gap:14px;align-items:center;padding:13px 0;border-bottom:1px solid var(--line)}.news time{font-size:14px;color:var(--mute)}
/* 로드맵 전체 */
.ph{padding:44px 0 24px}.ph h1{font-size:40px}.ph p{color:var(--sub);font-size:18px;margin-top:10px;max-width:760px}.src{display:flex;gap:8px 16px;flex-wrap:wrap;margin-top:16px;font-size:14px;color:var(--sub)}.src a{color:var(--ac);font-weight:600}
.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:14px;color:var(--sub);margin-top:14px}
.rs{display:grid;grid-template-columns:72px minmax(0,1fr);gap:0 24px;padding-bottom:12px}
.rs .rail{position:relative;display:flex;justify-content:center}.rs .rail::before{content:"";position:absolute;top:8px;bottom:-8px;width:3px;background:var(--ink);border-radius:2px}.rs:last-child .rail::before{bottom:60%}
.rs .num{position:relative;width:52px;height:52px;border-radius:50%;background:var(--ink);color:var(--bg);display:grid;place-items:center;font-size:20px;font-weight:800}
.rs .body{padding:6px 0 40px}.rs h2{font-size:26px}.rs .lede{color:var(--sub);margin-top:6px;max-width:760px}
.items{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:18px}
.it{border:1.5px solid var(--line2);border-radius:12px;padding:14px 16px;background:var(--bg);display:flex;flex-direction:column;gap:6px}.it:hover{border-color:var(--ac)}.it.here{border-color:var(--ac);box-shadow:0 0 0 3px var(--ac-s)}
.it b{font-size:16px;line-height:1.4}.it p{color:var(--sub);font-size:14px;line-height:1.5}.it .chips{margin-top:4px}
.flow{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px;list-style:none;padding:0;counter-reset:f}.flow li{counter-increment:f;display:flex;align-items:center;gap:8px;border:1.5px solid var(--line2);border-radius:99px;padding:6px 14px 6px 6px;font-weight:600;font-size:15px;background:var(--bg)}.flow li::before{content:counter(f);width:24px;height:24px;border-radius:50%;background:var(--paper);display:grid;place-items:center;font-size:12px;font-weight:800}
.checks{list-style:none;padding:0;margin:16px 0 0;display:flex;flex-direction:column;gap:6px}.checks li{display:flex;gap:10px;align-items:flex-start;font-size:15px;color:var(--sub)}.checks input{margin-top:5px;accent-color:var(--ac)}
.lecbox{margin-top:16px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:12px 14px;border-radius:10px;background:var(--lec-s)}.lecbox>span:first-child{font-size:14px;font-weight:700;color:var(--lec);display:flex;gap:6px;align-items:center}.lecbox .i{width:16px;height:16px}
/* 주제 */
.crumb{display:flex;gap:6px;align-items:center;flex-wrap:wrap;color:var(--sub);font-size:14px;padding:20px 0 0}.crumb .i{width:14px;height:14px}
.tp{display:grid;grid-template-columns:240px minmax(0,1fr) 240px;gap:44px;padding:24px 0 72px}
.lnav{position:sticky;top:84px;align-self:start;font-size:14px}.lnav h3{font-size:13px;color:var(--mute);font-weight:600;margin-bottom:8px}
.lnav ol{list-style:none;margin:0;padding:0}.lnav>ol>li>a{display:flex;gap:8px;padding:6px 8px;border-radius:7px;font-weight:600}.lnav>ol>li>a span{color:var(--mute);width:16px}
.lnav ul{list-style:none;margin:2px 0 6px 22px;padding:0 0 0 10px;border-left:2px solid var(--line)}.lnav ul a{display:block;padding:4px 8px;color:var(--sub);border-radius:6px}.lnav ul a[aria-current]{color:var(--ac);background:var(--ac-s);font-weight:700}
.kick{display:flex;gap:8px;align-items:center;flex-wrap:wrap;color:var(--sub);font-size:14px;font-weight:600}
.tp h1{font-size:38px;margin-top:8px;line-height:1.25}
.q{margin-top:14px;font-size:20px;line-height:1.5;padding:14px 18px;border-left:4px solid var(--ac);background:var(--ac-s);border-radius:0 10px 10px 0}
.pre{margin-top:32px;border:1.5px solid var(--lec);border-radius:16px;padding:20px;background:var(--lec-s)}
.pre-h{display:flex;justify-content:space-between;align-items:start;gap:12px;flex-wrap:wrap}.pre h2{font-size:20px;display:flex;gap:8px;align-items:center}.pre h2 .i{color:var(--lec);width:22px;height:22px}.pre p{color:var(--sub);font-size:15px;margin-top:4px}
.lcards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:16px}
.lcard{background:var(--bg);border:1px solid var(--line);border-radius:10px;overflow:hidden;display:flex;flex-direction:column}.lcard img{width:100%;aspect-ratio:16/9;object-fit:cover}.lcard div{padding:8px 10px 10px}.lcard b{display:block;font-size:13px;line-height:1.35}.lcard small{color:var(--mute);font-size:12px}
.know{list-style:none;margin:12px 0 0;padding:0;border-top:1px solid var(--line)}.know li{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,auto);gap:6px 16px;align-items:center;padding:11px 0;border-bottom:1px solid var(--line)}.know li>span{display:flex;gap:10px;align-items:baseline}.know li>span::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--ink);flex:none;transform:translateY(-2px)}
.doc{margin-top:8px}.doc h2{font-size:24px;margin:40px 0 12px;scroll-margin-top:80px}.doc h3{font-size:18px;margin:24px 0 8px}.doc p{margin:10px 0}.doc ul,.doc ol{padding-left:22px;margin:10px 0}.doc li{margin:4px 0}.doc a{color:var(--ac);text-decoration:underline;text-underline-offset:3px}
.doc code,.know code{font-size:.9em;background:var(--paper);border:1px solid var(--line);border-radius:5px;padding:0 5px}
.doc pre{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:14px;overflow:auto;font-size:14px}
.tw{overflow-x:auto;margin:14px 0}.doc table{border-collapse:collapse;width:100%;font-size:15px}.doc th,.doc td{text-align:left;padding:10px 12px 10px 0;border-bottom:1px solid var(--line);vertical-align:top}.doc th{border-bottom:2px solid var(--ink)}
.rrail{position:sticky;top:84px;align-self:start;display:flex;flex-direction:column;gap:16px;font-size:14px}
.toc h3,.srcbox h3{font-size:13px;color:var(--mute);font-weight:600;margin-bottom:6px}.toc a{display:block;padding:3px 0;color:var(--sub)}.toc a:hover{color:var(--ink)}
.srcbox{border:1px solid var(--line);border-radius:12px;padding:14px;background:var(--paper)}.srcbox p{color:var(--sub);line-height:1.55}.srcbox a{display:flex;gap:6px;align-items:center;color:var(--ac);font-weight:600;margin-top:8px}.srcbox a .i{width:15px;height:15px}
/* 강의 */
.cg{margin-top:28px}.cg-h{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;padding-bottom:10px;border-bottom:2px solid var(--ink)}.cg-h h2{font-size:22px}.cg-h small{color:var(--sub)}
.cl{list-style:none;margin:0;padding:0}.cl li{display:grid;grid-template-columns:44px minmax(0,1fr) minmax(0,.9fr);gap:16px;align-items:center;padding:12px 0;border-bottom:1px solid var(--line)}
.cl .no{font-family:"JetBrains Mono",monospace;color:var(--mute);font-weight:600}.cl b{display:block;line-height:1.4}.cl p{color:var(--sub);font-size:14px;line-height:1.5}.cl .chips{justify-content:flex-end}
/* 사례 */
.tabs{display:flex;gap:4px;border-bottom:1px solid var(--line);margin-top:8px;overflow-x:auto}.tabs a{padding:10px 14px;font-weight:700;color:var(--sub);border-bottom:3px solid transparent;white-space:nowrap}.tabs a[aria-current]{color:var(--ink);border-color:var(--ink)}.tabs small{color:var(--mute);font-weight:600;margin-left:4px}
.fl{display:flex;gap:6px;flex-wrap:wrap;margin:20px 0 4px}.fl button{border:1px solid var(--line);background:var(--bg);border-radius:99px;padding:5px 12px;font-size:14px;font-weight:600;cursor:pointer;color:var(--sub)}.fl button[aria-pressed=true]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:14px}
.cc{border:1px solid var(--line);border-radius:14px;padding:16px;display:flex;flex-direction:column;gap:8px;background:var(--bg)}.cc:hover{border-color:var(--ac)}
.cc .top{display:flex;justify-content:space-between;gap:8px;font-size:13px;color:var(--sub);font-weight:600}.cc b{font-size:16px;line-height:1.4}
.cc dl{display:grid;grid-template-columns:auto minmax(0,1fr);gap:2px 10px;margin:0;font-size:13px}.cc dt{color:var(--mute)}.cc dd{margin:0;color:var(--sub)}
.cc .ev{margin-top:auto;padding-top:10px;border-top:1px dashed var(--line);font-size:13px;font-weight:700;color:var(--sub)}.cc .ev.run{color:var(--lec)}
.res3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.rb{border:1px solid var(--line);border-radius:14px;padding:18px}.rb h3{font-size:18px;display:flex;gap:8px;align-items:center}.rb h3 .i{color:var(--ac)}.rb .big{font-size:34px;font-weight:800;margin-top:6px;letter-spacing:-.02em}.rb .big small{font-size:15px;color:var(--sub);font-weight:600;margin-left:4px}
.rb ul{list-style:none;padding:0;margin:10px 0 0;font-size:14px;color:var(--sub)}.rb li{padding:5px 0;border-top:1px solid var(--line)}.rb li b{color:var(--ink);font-weight:600}
.tk{width:100%;border-collapse:collapse}.tk td{padding:12px 16px 12px 0;border-bottom:1px solid var(--line);vertical-align:top}.tk td:first-child{color:var(--sub);width:40%}
.note{font-size:13px;color:var(--mute);margin-top:12px;line-height:1.55}
${DLG_CSS({ scrim: "rgba(10,12,16,.35)", bg: "var(--bg)", ink: "var(--ink)", line: "var(--line)", r: "12px", sub: "var(--sub)", hover: "var(--paper)" })}
@media (max-width:1180px){.tp{grid-template-columns:220px minmax(0,1fr)}.rrail{display:none}.sbtn{min-width:0}.sbtn span,.sbtn kbd{display:none}}
@media (max-width:1024px){.hero .wrap{grid-template-columns:1fr;gap:32px}.stg{grid-template-columns:repeat(3,minmax(0,1fr))}.grid2{grid-template-columns:1fr}.cards,.res3{grid-template-columns:repeat(2,minmax(0,1fr))}.lcards{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:860px){.tp{grid-template-columns:1fr}.lnav{position:static;display:none}.cl li{grid-template-columns:36px minmax(0,1fr)}.cl .chips{grid-column:2;justify-content:flex-start}.items{grid-template-columns:1fr}}
@media (max-width:700px){.wrap{padding:0 16px}.nav{display:none}.hero{padding:36px 0 32px}.hero h1{font-size:31px}.hero .def{font-size:16px}.stg,.cards,.res3{grid-template-columns:1fr}
.start td{display:block;width:auto!important;padding:2px 0;border:0}.start tr{display:block;padding:12px 0;border-bottom:1px solid var(--line)}.start tr:first-child td{border:0}.start tr:first-child{border-top:1px solid var(--line)}
.sec-h h2{font-size:24px}.ph h1,.tp h1{font-size:28px}.ph p{font-size:16px}.q{font-size:17px}.rs{grid-template-columns:40px minmax(0,1fr);gap:0 14px}.rs .num{width:36px;height:36px;font-size:16px}.rs h2{font-size:21px}
.news li{grid-template-columns:auto minmax(0,1fr)}.news time{grid-column:1/-1}.ft .wrap{grid-template-columns:1fr}.know li{grid-template-columns:1fr}.lcards{grid-template-columns:repeat(2,minmax(0,1fr))}}`;

/* 조각 */
const header = (cur) => `<header class="hd"><div class="wrap"><a class="brand" href="home.html"><span class="bm">${i("route")}</span>풀스택 AI/AX 엔지니어</a>
<nav class="nav" aria-label="메뉴">${[["로드맵", "roadmap.html"], ["강의", "lectures.html"], ["사례와 자료", "cases.html"], ["소식", "home.html#news"]].map(([t, h]) => `<a href="${h}"${t === cur ? ' aria-current="page"' : ""}>${t}</a>`).join("")}</nav>
<div class="tools"><button class="sbtn" data-search aria-label="찾기">${i("search")}<span>로드맵, 강의, 사례 찾기</span><kbd>/</kbd></button><button class="ibtn" data-theme-toggle aria-label="화면 밝기 바꾸기">${i("moon", "i moon-i")}${i("sun", "i sun-i")}</button></div></div></header>`;
const footer = `<footer class="ft"><div class="wrap"><div><b>공익 목적으로 만드는 공개 자료예요</b><p>가입이나 결제 없이 누구나 처음부터 끝까지 볼 수 있어요.</p><p>${COPY}</p></div>
<div><b>이 사이트는 두 레포를 읽어 만들어요</b><p>로드맵, 사례와 자료: ax-engineer-roadmap ${S.version} (MIT License)</p><p>강의: 강의 자료 레포의 슬라이드와 PDF (개인 학습에 자유롭게 보되, 허락 없이 옮겨 싣거나 고쳐 배포할 수 없어요)</p></div></div></footer>`;
const items = [
  ...S.stages.map((s) => ({ t: `${s.no}단계 ${s.title}`, s: "로드맵" })),
  ...S.stages[1].areas.map((a) => ({ t: a.t, s: "로드맵 2단계" })),
  ...chapters.map((c) => ({ t: `${c.no} ${c.title}`, s: "강의" })),
  ...S.cases.map((c) => ({ t: c.t, s: "사례" })),
];
const kit = searchKit(items, "topic.html");
const chip = (n) => { const c = byNo[n]; return `<a class="chip" href="lectures.html" title="${esc(c.title)}"><b>${n}</b>${esc(short(c.title))}</a>`; };
const chipS = (n) => { const c = byNo[n]; return `<span class="chip" title="${esc(c.title)}"><b>${n}</b>${esc(short(c.title))}</span>`; };
const short = (t) => t.replace(/\s*\(.*\)$/, "");
const lecIcon = i("book-open");

/* 홈 */
const home = html("풀스택 AI/AX 엔지니어", css, `${header("")}<main>
<section class="hero"><div class="wrap"><div><span class="lbl rm">${i("route")}공개 로드맵 ${S.version}</span>
<h1 style="margin-top:14px">AX 엔지니어로 가는 길과<br class="w"> 그 길에 필요한 기초 강의를<br class="w"> 한곳에 모았어요</h1>
<p class="def">${esc(S.defn)}</p>
<div class="btns"><a class="btn pri" href="roadmap.html">${i("route")}로드맵 보기</a><a class="btn" href="lectures.html">${lecIcon}기초 강의부터</a></div></div>
<div class="two" aria-label="로드맵과 강의가 이어지는 모양"><h3>로드맵 5단계</h3>
<div class="row rm">${S.stages.map((s) => `<span class="${s.no === 2 ? "on" : ""}">${s.no}. ${s.title.replace(/ 익히기| 이해하기| 넓히기| 만들기/, "")}</span>`).join("")}</div>
<div class="wire"><svg viewBox="0 0 400 34" preserveAspectRatio="none" aria-hidden="true"><g fill="none" stroke="var(--lec)" stroke-width="1.6" stroke-dasharray="4 3"><path d="M120 0 C120 18 40 16 40 34"/><path d="M120 0 C120 18 120 16 120 34"/><path d="M120 0 C120 18 200 16 200 34"/><path d="M200 0 C200 18 280 16 280 34"/><path d="M280 0 C280 18 360 16 360 34"/></g></svg></div>
<div class="row lc">${courseStages.map((s) => `<span>${esc(s.title.replace(/와 /, "·"))}</span>`).join("")}</div><h3 style="margin-top:8px">먼저 익힐 기초 강의</h3>
<p>로드맵 주제를 펼치면 그 주제를 읽기 전에 손에 익혀 둘 강의 챕터가 같이 나와요. 강의 쪽에서도 "이 챕터가 쓰이는 로드맵 주제"를 보여 줘요.</p></div></div></section>
<section class="sec"><div class="wrap"><div class="sec-h"><div><h2>나에게 맞는 시작점</h2><p>지금 내 경험과 가까운 줄에서 시작해요. 어느 경로든 첫 실습은 P1이에요.</p></div><a class="more" href="roadmap.html">로드맵 전체 ${i("arrow-right")}</a></div>
<table class="start"><tbody>${S.start.map((r) => `<tr><td>${esc(r.who)}</td><td>${esc(r.go)}</td><td>${esc(r.first)}</td></tr>`).join("")}</tbody></table></div></section>
<section class="sec"><div class="wrap"><div class="sec-h"><div><h2>로드맵 5단계</h2><p>단계마다 읽을 문서와 다음으로 넘어가기 전에 스스로 확인할 질문이 있어요.</p></div></div>
<div class="stg">${S.stages.map((s) => { const cnt = [s.docs && `문서 ${s.docs.length}개`, s.areas && `기술 ${s.areas.length}영역`, s.steps && `업무 전환 ${s.steps.length}단계`, s.projects && `실습 P1~P${s.projects.length}`, s.no === 5 && `업무 사례 ${S.cases.length}개`].find(Boolean);
  const nl = s.no === 2 ? Object.values(AREA_LINKS).flat() : STAGE_LINKS[s.no];
  const n = new Set(nl).size; return `<a class="stc" href="roadmap.html"><span class="n">${s.no}</span><h3>${esc(s.title)}</h3><span class="c">${cnt}</span><p>${esc(s.lede.split(". ")[0].replace(/\.$/, ""))}.</p><span class="lk${n ? "" : " none"}">${lecIcon}${n ? `이어진 강의 ${n}개` : "이어진 강의 없음"}</span></a>`; }).join("")}</div></div></section>
<section class="sec"><div class="wrap grid2"><div><div class="sec-h"><div><h2>업무 사례에서 시작해도 돼요</h2><p>원본 시스템, 승인 지점, 실패 대응을 업무마다 비교해요.</p></div><a class="more" href="cases.html">사례 ${S.cases.length}개 ${i("arrow-right")}</a></div>
${S.cases.slice(0, 4).map((c) => `<a class="case" href="cases.html"><span class="dots" title="난이도 ${c.diff}">${[1, 2, 3, 4, 5].map((k) => `<i class="${k <= c.diff ? "on" : ""}"></i>`).join("")}</span><b>${esc(c.t)}</b><small>${esc(c.area)} · ${esc(c.industry)} · 위험 ${esc(c.risk)} · ${esc(c.ev)}</small></a>`).join("")}</div>
<div class="hire"><h3>월간 채용 현황 · 2026년 10월</h3><p style="margin-top:2px;color:var(--sub);font-size:14px">잡코리아에서 모은 국내 AX·AI Agent·FDE 공고</p>
<div class="big">${S.hiring.rows.reduce((a, r) => a + r.n, 0)}<small>건</small></div>
<div class="bars">${S.hiring.rows.map((r) => `<div class="bar"><span>${r.type}</span><i style="width:${Math.round((r.n / 72) * 100)}%"></i><em>${r.n}</em></div>`).join("")}</div>
<p>${esc(S.hiring.note)} 공고별 책임과 요건은 사례와 자료에서 볼 수 있어요.</p></div></div></section>
<section class="sec" id="news"><div class="wrap"><div class="sec-h"><div><h2>소식</h2><p>로드맵과 강의에서 바뀐 내용을 한곳에 모아요.</p></div></div>
<ul class="news">${[["2026-11-24", "lc", "강의", "46 데이터 정리하기 (타이타닉 전처리)를 올렸어요"], ["2026-11-23", "lc", "강의", "모든 슬라이드에 PDF 받기를 더했어요"], ["2026-10-28", "rm", "로드맵", "공개 AX 실패·중단 사례 16개와 월간 채용 현황을 더했어요"], ["2026-10-27", "rm", "로드맵", `${S.version}: 업무 사례를 15개로 늘렸어요`]].map(([d, k, t, x]) => `<li><time>${d}</time><span class="lbl ${k}">${t}</span><span>${x}</span></li>`).join("")}</ul></div></section>
</main>${footer}`, kit);

/* 로드맵 전체 */
const stageBody = (s) => {
  let inner = "";
  if (s.docs) inner = `<div class="items">${s.docs.map((d) => `<a class="it" href="topic.html"><b>${esc(d.t)}</b><p>${esc(d.d)}</p></a>`).join("")}</div>`;
  if (s.areas) inner = `<div class="items">${s.areas.map((a) => `<a class="it${a.id === "software-and-api" ? " here" : ""}" href="topic.html"><b>${esc(a.t)}</b><p>${esc(a.q)}</p><span class="chips">${AREA_LINKS[a.id].slice(0, 4).map(chipS).join("")}${AREA_LINKS[a.id].length > 4 ? `<span class="chip">외 ${AREA_LINKS[a.id].length - 4}개</span>` : ""}${SOON[a.id] ? `<span class="chip soon">${SOON[a.id]}</span>` : ""}</span></a>`).join("")}</div>`;
  if (s.steps) inner = `<ol class="flow">${s.steps.map((x) => `<li>${esc(x.t)}</li>`).join("")}</ol>`;
  if (s.projects) inner = `<div class="items">${s.projects.map((p) => `<a class="it" href="topic.html"><b>${esc(p.t)}</b><p>${esc(p.out)}</p></a>`).join("")}</div>`;
  if (s.no === 5) inner = `<div class="items">${S.cases.slice(0, 4).map((c) => `<a class="it" href="cases.html"><b>${esc(c.t)}</b><p>${esc(c.area)} · 난이도 ${c.diff} · ${esc(c.ev)}</p></a>`).join("")}</div>`;
  const lk = STAGE_LINKS[s.no];
  const lec = lk && lk.length ? `<div class="lecbox"><span>${lecIcon}먼저 익힐 기초</span><span class="chips">${lk.map(chip).join("")}</span></div>` : "";
  const ch = s.checks.length ? `<ul class="checks">${s.checks.map((c, k) => `<li><input type="checkbox" id="k${s.no}${k}"><label for="k${s.no}${k}">${esc(c)}</label></li>`).join("")}</ul>` : "";
  return inner + lec + ch;
};
const roadmap = html("로드맵 · 풀스택 AI/AX 엔지니어", css, `${header("로드맵")}<main class="wrap">
<section class="ph"><span class="lbl rm">${i("route")}로드맵</span><h1 style="margin-top:12px">AX 엔지니어 로드맵 5단계</h1><p>직무를 이해하고, 기술 기초를 익히고, 업무를 바꾸는 순서를 배운 뒤, 프로젝트와 사례로 넓혀요. 초록 칩은 그 주제 전에 손에 익혀 두면 좋은 기초 강의예요.</p>
<div class="src"><span>원문 <a href="${GH("README.md")}">woogi-kang/ax-engineer-roadmap</a></span><span>${S.version} · ${S.commit}</span><span>MIT License</span></div>
<div class="legend"><span class="chip"><b>36</b>기초 강의</span><span class="chip soon">강의 준비 중</span><span>체크 표시는 이 화면에서만 보이고 저장하지 않아요</span></div></section>
${S.stages.map((s) => `<section class="rs" id="s${s.no}"><div class="rail"><span class="num">${s.no}</span></div><div class="body"><h2>${esc(s.title)}</h2><p class="lede">${esc(s.lede)}</p>${stageBody(s)}</div></section>`).join("")}
</main>${footer}`, kit);

/* 주제 화면: 2단계 소프트웨어와 API. 본문은 로드맵 레포 문서를 그대로 그려요 */
const mdi = (s) => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/\[([^\]]+)\]\(([^)]+)\)/g, (m, t, h) => `<a href="${h.startsWith("http") ? h : GH("technical-foundations/" + h)}">${t}</a>`);
const render = (src) => {
  const L = src.split("\n"); let o = "", k = 0; const ids = [];
  while (k < L.length) {
    const l = L[k];
    if (l.startsWith("```")) { let b = []; k++; while (k < L.length && !L[k].startsWith("```")) b.push(L[k++]); o += `<pre><code>${esc(b.join("\n"))}</code></pre>`; k++; continue; }
    if (/^## /.test(l)) { const t = l.slice(3); const id = "h" + ids.length; ids.push([id, t]); o += `<h2 id="${id}">${esc(t)}</h2>`; k++; continue; }
    if (/^### /.test(l)) { o += `<h3>${esc(l.slice(4))}</h3>`; k++; continue; }
    if (/^\|/.test(l)) { const rows = []; while (k < L.length && /^\|/.test(L[k])) rows.push(L[k++]); const r = rows.filter((x) => !/^\|[\s|:-]+\|$/.test(x)).map((x) => x.slice(1, -1).split("|").map((c) => c.trim()));
      o += `<div class="tw"><table><thead><tr>${r[0].map((c) => `<th>${mdi(c)}</th>`).join("")}</tr></thead><tbody>${r.slice(1).map((x) => `<tr>${x.map((c) => `<td>${mdi(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`; continue; }
    if (/^- /.test(l)) { let b = []; while (k < L.length && /^- /.test(L[k])) b.push(L[k++].slice(2)); o += `<ul>${b.map((x) => `<li>${mdi(x)}</li>`).join("")}</ul>`; continue; }
    if (/^\d+\. /.test(l)) { let b = []; while (k < L.length && /^\d+\. /.test(L[k])) b.push(L[k++].replace(/^\d+\. /, "")); o += `<ol>${b.map((x) => `<li>${mdi(x)}</li>`).join("")}</ol>`; continue; }
    if (l.trim()) { let b = []; while (k < L.length && L[k].trim() && !/^(#|\||- |\d+\. |```)/.test(L[k])) b.push(L[k++]); o += `<p>${mdi(b.join(" "))}</p>`; continue; }
    k++;
  }
  return { o, ids };
};
const A = S.stages[1].areas[0];
const parts = S.topicMd.split(/\n(?=## )/);
const title = parts[0].replace(/^# /, "").trim();
const sec = Object.fromEntries(parts.slice(1).map((p) => [p.split("\n")[0].slice(3), p]));
const knowItems = [...sec["알아야 할 것"].matchAll(/^- (.+)$/gm)].map((m) => m[1]);
const rest = render(parts.slice(1).filter((p) => !p.startsWith("## 알아야 할 것")).join("\n"));
const allLec = AREA_LINKS[A.id];
const topic = html(`${title} · 로드맵`, css, `${header("로드맵")}<main class="wrap">
<nav class="crumb" aria-label="현재 위치"><a href="roadmap.html">로드맵</a>${i("chevron-right")}<a href="roadmap.html#s2">2단계 기술 기초 익히기</a>${i("chevron-right")}<span>${esc(title)}</span></nav>
<div class="tp"><nav class="lnav" aria-label="로드맵 단계"><h3>로드맵 5단계</h3><ol>${S.stages.map((s) => `<li><a href="roadmap.html#s${s.no}"><span>${s.no}</span>${esc(s.title)}</a>${s.no === 2 ? `<ul>${s.areas.map((a) => `<li><a href="topic.html"${a.id === A.id ? ' aria-current="page"' : ""}>${esc(a.t)}</a></li>`).join("")}</ul>` : ""}</li>`).join("")}</ol></nav>
<article><p class="kick"><span class="lbl rm">${i("route")}로드맵 2단계</span>기술 기초 7영역 중 1</p><h1>${esc(title)}</h1><p class="q">${esc(A.q)}</p>
<section class="pre" aria-label="먼저 익힐 기초"><div class="pre-h"><div><h2>${lecIcon}먼저 익힐 기초 강의</h2><p>이 문서를 읽기 전에 손으로 한 번씩 해 보면 좋은 챕터예요. 슬라이드와 PDF로 바로 볼 수 있어요.</p></div><a class="more" href="lectures.html">강의 전체 ${i("arrow-right")}</a></div>
<div class="lcards">${allLec.slice(0, 8).map((n) => byNo[n]).map((c) => `<a class="lcard" href="${deck(c)}"><img src="../shared/covers/${c.no}.jpg" alt="" loading="lazy"><div><b>${c.no} · ${esc(short(c.title))}</b><small>${esc(c.track)}</small></div></a>`).join("")}</div></section>
<div class="doc"><h2 id="know">알아야 할 것</h2><p style="color:var(--sub);font-size:15px">줄마다 오른쪽 칩이 이 내용을 다루는 강의예요. 칩이 없는 줄은 강의를 준비하고 있어요.</p>
<ul class="know">${knowItems.map((x, k) => `<li><span>${mdi(x)}</span><span class="chips">${ITEM_LINKS[k]?.length ? ITEM_LINKS[k].map(chip).join("") : `<span class="chip soon">강의 준비 중</span>`}</span></li>`).join("")}</ul>
${rest.o}</div></article>
<aside class="rrail"><div class="toc"><h3>이 문서의 차례</h3><a href="#know">알아야 할 것</a>${rest.ids.map(([id, t]) => `<a href="#${id}">${esc(t)}</a>`).join("")}</div>
<div class="srcbox"><h3>원문</h3><p>본문은 ax-engineer-roadmap의 문서를 빌드할 때 그대로 가져와요. ${S.version} · ${S.commit} · MIT License</p><a href="${GH(A.href)}">${i("external-link")}GitHub에서 보기</a><a href="https://github.com/woogi-kang/ax-engineer-roadmap/issues">${i("message-square")}고치기 제안</a></div></aside></div></main>${footer}`, kit);

/* 강의 */
const lectures = html("강의 · 풀스택 AI/AX 엔지니어", css, `${header("강의")}<main class="wrap">
<section class="ph"><span class="lbl lc">${lecIcon}강의</span><h1 style="margin-top:12px">로드맵을 따라가기 위한 기초 강의 ${chapters.length}개</h1><p>터미널부터 데이터 분석까지 배우는 순서대로 놓았어요. 오른쪽 칩은 이 챕터를 "먼저 익힐 기초"로 쓰는 로드맵 주제예요.</p></section>
${courseStages.map((s) => `<section class="cg"><div class="cg-h"><h2>${esc(s.title)}</h2><small>${s.from}~${s.to} · ${s.list.length}개</small></div><ul class="cl">${s.list.map((c) => `<li><span class="no">${c.no}</span><a href="../v2/chapter.html"><b>${esc(c.title)}</b><p>${md(c.goal)}</p></a><span class="chips">${(usedBy[c.no] || []).slice(0, 3).map((t) => `<span class="chip">${i("route")}${esc(t)}</span>`).join("")}</span></li>`).join("")}</ul></section>`).join("")}
<p class="note" style="margin:24px 0 56px">챕터를 누르면 지금처럼 슬라이드 플레이어와 README가 있는 챕터 화면으로 가요. 로드맵과 강의를 잇는 표는 초안이에요.</p></main>${footer}`, kit);

/* 사례와 자료 */
const areas = [...new Set(S.cases.map((c) => c.area))];
const cases = html("사례와 자료 · 풀스택 AI/AX 엔지니어", css, `${header("사례와 자료")}<main class="wrap">
<section class="ph"><span class="lbl rm">${i("layers")}사례와 자료</span><h1 style="margin-top:12px">업무 사례, 공개 사례, 템플릿, 채용 현황</h1><p>로드맵 5단계에서 쓰는 자료를 모았어요. 실제 조직의 운영 성과가 아니라 실습용 설계와 공개된 발표를 구분해 보여 줘요.</p>
<nav class="tabs" aria-label="자료 종류"><a href="#cases" aria-current="page">업무 사례<small>${S.cases.length}</small></a><a href="#public">공개 사례<small>${S.publicCases.n}</small></a><a href="#fail">실패·중단 사례<small>${S.failures.n}</small></a><a href="#tk">실무 템플릿<small>${S.toolkit.reduce((a, t) => a + t.items.length, 0)}</small></a><a href="#hire">채용 현황</a></nav></section>
<section id="cases"><div class="fl" data-fl><button aria-pressed="true" data-a="all">전체</button>${areas.map((a) => `<button aria-pressed="false" data-a="${a}">${a}</button>`).join("")}</div>
<div class="cards">${S.cases.map((c) => `<a class="cc" href="#" data-area="${c.area}"><span class="top"><span>${esc(c.area)} · ${esc(c.industry)}</span><span class="dots" title="난이도 ${c.diff}">${[1, 2, 3, 4, 5].map((k) => `<i class="${k <= c.diff ? "on" : ""}"></i>`).join("")}</span></span><b>${esc(c.t)}</b>
<dl><dt>위험</dt><dd>${esc(c.risk)}</dd><dt>실행 범위</dt><dd>${esc(c.scope)}</dd><dt>설계 단계</dt><dd>${esc(c.p)}</dd></dl><span class="ev${c.ev.includes("시뮬레이션") ? " run" : ""}">${esc(c.ev)}</span></a>`).join("")}</div>
<p class="note">준비 상태는 문서를 실습에 쓸 수 있다는 뜻이에요. 실제 조직에서 운영 성과를 검증했다는 뜻이 아니에요.</p></section>
<section class="sec" id="public" style="margin-top:40px"><div class="res3">
<div class="rb"><h3>${i("building-2")}국내외 공개 사례</h3><div class="big">${S.publicCases.n}<small>개 · 국내 ${S.publicCases.kr}개</small></div><ul>${S.publicCases.sample.slice(0, 4).map((c) => `<li><b>${esc(c.org)}</b> · ${esc(c.w)}</li>`).join("")}</ul></div>
<div class="rb" id="fail"><h3>${i("triangle-alert")}실패·중단 사례</h3><div class="big">${S.failures.n}<small>개 · 국내 ${S.failures.kr}개</small></div><ul><li>무엇을 바꾸려다 왜 멈췄는지</li><li>캡스톤 설계 점검표 여덟 질문</li><li>업무 사례마다 연결한 점검 항목</li></ul></div>
<div class="rb" id="hire"><h3>${i("chart-column")}월간 채용 현황</h3><div class="big">${S.hiring.rows.reduce((a, r) => a + r.n, 0)}<small>건 · 2026년 10월</small></div><ul>${S.hiring.rows.map((r) => `<li><b>${r.type}</b> · ${r.n}건 (모집 중 ${r.open})</li>`).join("")}</ul></div></div>
<p class="note">공개 사례는 외부 조직의 발표와 보도예요. 채용 공고 수는 재게시와 프로젝트 공고가 섞여 고유 채용 수가 아니에요.</p></section>
<section class="sec" id="tk"><div class="sec-h"><div><h2>실무 템플릿</h2><p>업무를 바꿀 때 빠뜨리기 쉬운 판단과 책임을 정리하는 양식이에요.</p></div></div>
<table class="tk"><tbody>${S.toolkit.map((t) => `<tr><td>${esc(t.when)}</td><td><span class="chips">${t.items.map((x) => `<a class="chip" href="#">${i("file-text")}${esc(x)}</a>`).join("")}</span></td></tr>`).join("")}</tbody></table></section>
</main>${footer}<script>(()=>{const bs=document.querySelectorAll('[data-fl] button');bs.forEach(b=>b.onclick=()=>{bs.forEach(x=>x.setAttribute('aria-pressed',x===b));document.querySelectorAll('[data-area]').forEach(c=>c.hidden=b.dataset.a!=='all'&&c.dataset.area!==b.dataset.a)})})()</script>`, kit);

write("v9", "home.html", home);
write("v9", "roadmap.html", roadmap);
write("v9", "topic.html", topic);
write("v9", "lectures.html", lectures);
write("v9", "cases.html", cases);
console.log("v9 ok");
