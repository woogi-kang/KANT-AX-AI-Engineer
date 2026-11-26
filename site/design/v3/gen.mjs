// 시안 v3 "코드 에디터": 어두운 바탕, 레포 폴더 나무와 터미널 창으로 그려요. site 폴더에서 node design/v3/gen.mjs
import { HERO_T, HERO_P, CTA1, CTA2, whoHtml, i, tile, esc, inline, chapters, stages, extras, news, NOTICE, C, goals, before, parts, slides, prev, next, cut, page, FOOT, write, LV } from "../lib.mjs";

const css = `
.who{margin-top:28px;border:1px solid var(--line);border-radius:10px;background:var(--panel);padding:22px}
.who-h{display:flex;gap:16px;align-items:baseline;flex-wrap:wrap}.who-h h2{font:700 15px "JetBrains Mono","D2Coding Hangul",monospace}.who-h h2::before{content:"# ";color:var(--prompt)}.who-h p{color:var(--sub);font-size:14px}
.who-g{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin-top:16px}
.who-i .i{width:20px;height:20px;color:var(--accent)}.who-i b{display:block;margin-top:8px;font-size:15px}.who-i p{font-size:13px;color:var(--sub);margin-top:2px}
.pr{list-style:none;margin:18px 0 0;padding:14px 0 0;border-top:1px solid var(--line);display:flex;flex-wrap:wrap;gap:8px 20px;font:13px "JetBrains Mono","D2Coding Hangul",monospace;color:var(--sub)}
.pr li{display:flex;gap:6px;align-items:center}.pr .i{width:15px;height:15px;color:var(--prompt)}
@media (max-width:760px){.who-g{grid-template-columns:1fr;gap:14px}}

:root{--bg:#0E1116;--panel:#151920;--panel-2:#1A1F27;--line:#252B35;--line-2:#323A46;--ink:#E7E9EE;--sub:#AEB5C1;--muted:#7D8594;--faint:#535B69;
 --accent:#6E9BF0;--accent-soft:#1B2740;--prompt:#7EE2A0;
 --t-term:#BAC0CA;--t-git:#E9A956;--t-gh:#A894EC;--t-py:#72A5E8;--t-docker:#56BFC8;--t-db:#E58BB8;color-scheme:dark}
:root[data-theme="light"]{--bg:#F6F5F1;--panel:#FFFFFF;--panel-2:#F1EFE9;--line:#E3E0D8;--line-2:#CBC7BC;--ink:#1D2330;--sub:#485062;--muted:#6A7180;--faint:#A3A8B2;--accent:#2459C9;--accent-soft:#E6EDFB;--prompt:#1F8A4C;
 --t-term:#3F4757;--t-git:#A0560A;--t-gh:#5A3BB8;--t-py:#1E5FA8;--t-docker:#0D7480;--t-db:#A23B72;color-scheme:light}
body{background:var(--bg);color:var(--ink);font-size:15px;line-height:1.6}
.wrap{max-width:1248px;margin:0 auto;padding:0 24px}
.t-term{--c:var(--t-term)}.t-git{--c:var(--t-git)}.t-gh{--c:var(--t-gh)}.t-py{--c:var(--t-py)}.t-docker{--c:var(--t-docker)}.t-db{--c:var(--t-db)}
.logo-tile{--sz:28px;width:var(--sz);height:var(--sz);border-radius:6px;background:#fff;display:grid;place-items:center;flex:none}.logo-tile svg{width:60%;height:60%}
/* 머리 */
.hd{position:sticky;top:0;z-index:20;height:52px;background:var(--bg);border-bottom:1px solid var(--line)}
.hd .wrap{height:100%;display:flex;align-items:center;gap:24px}.hd.full .wrap{max-width:none}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;font-size:15px;white-space:nowrap}
.mark{width:28px;height:28px;border-radius:6px;background:var(--accent);color:#0E1116;display:grid;place-items:center;font:800 13px/1 "JetBrains Mono",monospace;letter-spacing:-.06em}
:root[data-theme="light"] .mark{color:#fff}
.brand small{font-weight:500;color:var(--muted);font-size:inherit}
.nav{display:flex;height:100%}.nav a{display:flex;align-items:center;padding:0 14px;font-size:14px;color:var(--muted);border-bottom:2px solid transparent;margin-bottom:-1px}
.nav a:hover{color:var(--ink)}.nav a[aria-current]{color:var(--ink);border-color:var(--accent)}
.hd-r{margin-left:auto;display:flex;gap:6px;align-items:center}
.sbtn{display:flex;align-items:center;gap:8px;height:32px;width:260px;padding:0 8px 0 10px;border:1px solid var(--line-2);border-radius:6px;background:var(--panel);color:var(--muted);font-size:13px;cursor:pointer}
.sbtn span{flex:1;text-align:left}
kbd{font-size:11px;border:1px solid var(--line-2);border-radius:4px;padding:1px 5px;color:var(--sub)}
.ib{width:32px;height:32px;border:0;border-radius:6px;background:none;color:var(--muted);display:grid;place-items:center;cursor:pointer}.ib:hover{background:var(--panel-2);color:var(--ink)}
.om{display:none}
@media (max-width:760px){.nav,.sbtn span,.sbtn kbd{display:none}.sbtn{width:32px;border:0;background:none;padding:0;justify-content:center}.om{display:grid}.hd-r{gap:0}}
/* 첫 화면 */
.hero{display:grid;grid-template-columns:minmax(0,1fr) 440px;gap:48px;padding:56px 0 40px;align-items:center}
.hero .k{font:500 13px/1 "JetBrains Mono",monospace;color:var(--prompt)}
.hero h1{font-size:36px;line-height:1.3;letter-spacing:-.035em;font-weight:800;margin-top:14px}
.hero p{color:var(--sub);font-size:17px;margin-top:16px;max-width:30em}
.cta{display:flex;gap:10px;margin-top:28px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:8px;height:42px;padding:0 18px;border-radius:6px;font-weight:600;font-size:15px;border:1px solid var(--line-2);white-space:nowrap}
.btn.p{background:var(--accent);border-color:var(--accent);color:#0E1116}:root[data-theme="light"] .btn.p{color:#fff}
.btn.s{background:var(--panel)}.btn.sm{height:32px;padding:0 12px;font-size:13px}
.tree{background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;font:13px/1.5 "JetBrains Mono","D2Coding Hangul",monospace}
.tree-h{display:flex;align-items:center;gap:8px;padding:10px 14px;border-bottom:1px solid var(--line);color:var(--muted);font-size:12px;letter-spacing:.04em}
.tree ul{list-style:none;margin:0;padding:6px 0}
.tree li a{display:flex;align-items:center;gap:8px;padding:4px 14px;color:var(--sub);white-space:nowrap;overflow:hidden}
.tree li a:hover{background:var(--panel-2);color:var(--ink)}
.tree li.f a{padding-left:38px;color:var(--muted)}.tree li.f .i{color:var(--c);width:15px;height:15px}
.tree li a small{margin-left:auto;color:var(--faint)}
.tree .i{width:16px;height:16px}.tree .d .i{color:var(--accent)}
.notice{display:flex;gap:12px;align-items:center;padding:10px 14px;border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:6px;background:var(--panel);font-size:14px;color:var(--sub)}
.notice b{color:var(--ink);font-weight:600;white-space:nowrap}
/* 강의 */
.sec{padding-top:56px}
.sec-h{display:flex;align-items:baseline;gap:12px;margin-bottom:18px;flex-wrap:wrap}
.sec-h h2{font-size:22px;font-weight:800;letter-spacing:-.02em}
.sec-h .c{font:13px "JetBrains Mono",monospace;color:var(--faint)}
.sec-h .more{margin-left:auto;color:var(--accent);font-size:14px;display:flex;align-items:center;gap:4px}
.filters{display:flex;gap:6px;overflow-x:auto;padding:2px;margin-bottom:8px;scrollbar-width:none}
.filters button{height:30px;padding:0 12px;border-radius:6px;border:1px solid var(--line-2);background:none;color:var(--sub);font-size:13px;cursor:pointer;white-space:nowrap;display:flex;align-items:center;gap:6px}
.filters button i{width:8px;height:8px;border-radius:2px;background:var(--c)}
.filters button[aria-pressed="true"]{background:var(--ink);border-color:var(--ink);color:var(--bg)}
.stage{padding-top:36px}
.stage-h{display:flex;align-items:baseline;gap:10px;margin-bottom:14px;font:14px "JetBrains Mono","D2Coding Hangul",monospace;color:var(--muted);flex-wrap:wrap}
.stage-h b{font-family:"Pretendard",sans-serif;font-size:18px;color:var(--ink);font-weight:800;letter-spacing:-.02em}
.stage-h .p{color:var(--prompt)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
.card{display:flex;flex-direction:column;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;transition:border-color .2s,transform .2s cubic-bezier(.25,.8,.25,1)}
.card:hover{border-color:var(--c);transform:translateY(-2px)}
.card-top{display:flex;align-items:center;gap:8px;height:36px;padding:0 10px 0 12px;border-bottom:1px solid var(--line);font:12px "JetBrains Mono",monospace;color:var(--muted)}
.card-top>span:first-child{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.card-top .logo-tile{--sz:22px}
.card-code{background:var(--bg);padding:22px 14px;font:500 17px/1.3 "JetBrains Mono","D2Coding Hangul",monospace;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-bottom:1px solid var(--line)}
.card-code .p{color:var(--c);margin-right:10px}
.card-b{padding:14px;display:flex;flex-direction:column;gap:8px;flex:1}
.card-b h3{font-size:15px;font-weight:700;line-height:1.45;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.meta{margin-top:auto;display:flex;gap:8px;align-items:center;font-size:12px;color:var(--muted);min-width:0}
.meta .l{color:var(--c);white-space:nowrap}.meta .l i{font-style:normal;font-family:"JetBrains Mono",monospace;letter-spacing:-1px;margin-right:4px}.meta span:last-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.new{font:600 11px "Pretendard";color:var(--prompt);border:1px solid currentColor;border-radius:4px;padding:0 5px;margin-left:6px;vertical-align:2px;white-space:nowrap}
.tips{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}
.tip{display:flex;gap:14px;padding:18px;background:var(--panel);border:1px solid var(--line);border-radius:10px}
.tip .ic{width:40px;height:40px;border-radius:8px;background:var(--panel-2);color:#E2A64B;display:grid;place-items:center;flex:none}
.tip h3{font-size:15px;font-weight:700}.tip p{font-size:13px;color:var(--sub);margin-top:4px}
.rel{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}.rel span{font:12px "JetBrains Mono","D2Coding Hangul",monospace;color:var(--muted);background:var(--panel-2);border-radius:4px;padding:2px 6px}
.log{border:1px solid var(--line);border-radius:10px;background:var(--panel);overflow:hidden}
.log a{display:grid;grid-template-columns:96px 80px minmax(0,1fr);gap:14px;align-items:baseline;padding:14px 16px;border-bottom:1px solid var(--line);font-size:14px}
.log a:last-child{border-bottom:0}.log a:hover{background:var(--panel-2)}
.log time{font:12px "JetBrains Mono",monospace;color:var(--faint)}.log .k{font-size:12px;color:var(--accent);font-weight:600}
.log b{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
@media (max-width:640px){.log a{grid-template-columns:1fr;gap:2px}}
.ft{margin-top:64px;border-top:1px solid var(--line);padding:24px 0 40px;font-size:12px;color:var(--faint)}
.ft .wrap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}.ft nav{display:flex;gap:16px}
@media (max-width:1000px){.hero{grid-template-columns:1fr}.tree{max-width:520px}}
@media (max-width:640px){.wrap{padding:0 16px}.hero{padding:32px 0 28px;gap:28px}.hero h1{font-size:28px}.hero p{font-size:15px}.cta .btn{flex:1;justify-content:center}.grid{grid-template-columns:1fr;gap:12px}.card-code{padding:16px 12px;font-size:15px}.notice{align-items:flex-start}}
/* 찾기 창 */
.dlg{position:fixed;inset:0;z-index:50;background:rgba(0,0,0,.55);display:none;justify-content:center;align-items:flex-start;padding:12vh 16px 0}.dlg[open]{display:flex}
.dlg-box{width:min(620px,100%);background:var(--panel);border:1px solid var(--line-2);border-radius:10px;overflow:hidden}
.dlg-in{display:flex;gap:10px;align-items:center;padding:0 14px;height:52px;border-bottom:1px solid var(--line)}.dlg-in input{flex:1;min-width:0;background:none;border:0;outline:0;color:var(--ink);font:16px "JetBrains Mono","D2Coding Hangul",monospace}
.dlg-list{padding:6px;max-height:50vh;overflow:auto}.dlg-item{display:flex;gap:10px;padding:8px 10px;border-radius:6px;font-size:14px}.dlg-item b{flex:1;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.dlg-item small{color:var(--muted);white-space:nowrap}
.dlg-item.on,.dlg-item:hover{background:var(--accent-soft)}.dlg-empty{padding:20px;text-align:center;color:var(--muted)}
/* 장 화면 */
.ide{display:grid;grid-template-columns:260px minmax(0,1fr);min-height:calc(100vh - 52px)}
.exp{position:sticky;top:52px;height:calc(100vh - 52px);overflow:auto;background:var(--panel);border-right:1px solid var(--line);font:13px/1.5 "JetBrains Mono","D2Coding Hangul",monospace}
.exp-h{padding:12px 14px;font-size:11px;letter-spacing:.08em;color:var(--muted);border-bottom:1px solid var(--line)}
.exp details{border-bottom:1px solid var(--line)}.exp summary{list-style:none;display:flex;gap:6px;align-items:center;padding:8px 10px;color:var(--sub);cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.exp summary::-webkit-details-marker{display:none}.exp summary .i{width:15px;height:15px;color:var(--accent)}
.exp ol{list-style:none;margin:0;padding:0 0 6px}.exp li a{display:flex;gap:8px;padding:4px 10px 4px 30px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.exp li a span{color:var(--faint);min-width:18px;text-align:right}.exp li a:hover{color:var(--ink);background:var(--panel-2)}
.exp li a[aria-current]{color:var(--ink);background:var(--accent-soft);box-shadow:inset 2px 0 var(--accent)}
.ed{min-width:0}
.tabs{display:flex;background:var(--panel);border-bottom:1px solid var(--line);overflow-x:auto;scrollbar-width:none}
.tabs a{display:flex;gap:8px;align-items:center;padding:0 16px;height:40px;font:13px "JetBrains Mono",monospace;color:var(--muted);border-right:1px solid var(--line);white-space:nowrap}
.tabs a[aria-current]{background:var(--bg);color:var(--ink);box-shadow:inset 0 2px var(--accent)}.tabs .i{width:15px;height:15px}
.ed-in{max-width:1080px;margin:0 auto;padding:24px 28px 0}
.ed-h{display:flex;gap:16px;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;margin-bottom:18px}
.ed-h .k{font:13px "JetBrains Mono","D2Coding Hangul",monospace;color:var(--c)}
.ed-h h1{font-size:28px;font-weight:800;letter-spacing:-.03em;margin-top:4px}
.ed-h p{color:var(--sub);margin-top:4px}
.ed-h .act{display:flex;gap:8px}
.player{aspect-ratio:16/9;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:#000}.player iframe{width:100%;height:100%;border:0}
.keys{display:flex;gap:16px;flex-wrap:wrap;margin-top:10px;font-size:12px;color:var(--muted)}
.md{margin-top:36px;border:1px solid var(--line);border-radius:10px;background:var(--panel)}
.md-h{display:flex;gap:8px;align-items:center;padding:10px 16px;border-bottom:1px solid var(--line);font:12px "JetBrains Mono",monospace;color:var(--muted)}
.md-b{padding:8px 24px 24px;line-height:1.75}
.md-b h2{font-size:18px;font-weight:800;margin:24px 0 10px}.md-b h2::before{content:"## ";color:var(--faint);font-family:"JetBrains Mono",monospace;font-weight:500}
.md-b ul{margin:0;padding-left:1.2em}.md-b li{margin:3px 0}
.md-b code{font-size:.86em;background:var(--panel-2);border:1px solid var(--line);border-radius:4px;padding:1px 5px;white-space:nowrap}
.md-b .tw{overflow-x:auto;border:1px solid var(--line);border-radius:8px}.md-b table{width:100%;border-collapse:collapse;font-size:14px}.md-b th,.md-b td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line)}.md-b th{color:var(--muted);font-weight:600;font-size:13px}.md-b tr:last-child td{border-bottom:0}
.pn{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:24px}.pn a{padding:14px 16px;border:1px solid var(--line);border-radius:10px;background:var(--panel)}.pn a:hover{border-color:var(--accent)}
.pn small{display:block;font:12px "JetBrains Mono",monospace;color:var(--muted)}.pn b{font-size:14px;font-weight:600}.pn a:last-child{text-align:right}
@media (max-width:960px){.ide{grid-template-columns:1fr}.exp{display:none}}
@media (max-width:640px){.ed-in{padding:16px 16px 0}.ed-h h1{font-size:22px}.ed-h .act{width:100%}.ed-h .act .btn{flex:1;justify-content:center}.keys{display:none}.md-b{padding:4px 16px 16px}.pn{grid-template-columns:1fr}.pn a:last-child{text-align:left}}
`;
const PROMPT = { term: "$", git: "$", gh: "$", docker: "$", py: ">>>", db: "=#" };
const header = (full = false, side = false) => `<header class="hd${full ? " full" : ""}"><div class="wrap">
${side ? `<button class="ib" type="button" aria-label="목차 접기">${i("panel-left")}</button>` : ""}<a class="brand" href="home.html"><span class="mark">&gt;_</span><span>풀스택 AI/AX <small>엔지니어</small></span></a>
<nav class="nav"><a href="home.html#lec" aria-current="page">강의</a><a href="home.html#tips">꿀팁</a><a href="home.html#news">소식</a></nav>
<div class="hd-r"><button class="sbtn" type="button" data-search>${i("search")}<span>강의 찾기</span><kbd>Ctrl K</kbd></button><button class="ib" type="button" data-theme-toggle aria-label="밝게 보기">${i("sun")}</button><button class="ib om" type="button" aria-label="메뉴">${i("menu")}</button></div></div></header>`;
const foot = `<footer class="ft"><div class="wrap"><span>${FOOT}</span><nav><a href="#">이용 안내</a><a href="mailto:woogi@memoriz.net">문의</a></nav></div></footer>`;
const card = (c) => `<a class="card t-${c.tk}" href="chapter.html" data-t="${c.tk}"><div class="card-top"><span>${c.dir}/</span>${c.logos.map((k) => tile(k, 22)).join("")}</div><div class="card-code"><span class="p">${PROMPT[c.tk]}</span>${esc(c.keyword)}</div><div class="card-b"><h3>${esc(c.title)}${c.no === "46" ? '<span class="new">새 챕터</span>' : ""}</h3><div class="meta"><span class="l"><i>${"▮".repeat(LV[c.level])}${"▯".repeat(3 - LV[c.level])}</i>${c.level}</span><span>${esc(c.group)}</span></div></div></a>`;
const tracks = [["전체", "all", chapters.length], ...["터미널", "Git", "GitHub", "파이썬", "Docker", "데이터베이스"].map((t) => { const k = chapters.find((c) => c.track === t).tk; return [t, k, chapters.filter((c) => c.tk === k).length]; })];
const tree = `<div class="tree" aria-label="배우는 순서"><div class="tree-h">${i("folder-open")}배우는 순서</div><ul>
${stages.map((s) => `<li class="d"><a href="#stage-${s.no}">${i(s.no === 1 ? "folder-open" : "folder")}${s.no}-${esc(s.title.replace(/ /g, "-"))}/<small>${s.list.length}</small></a></li>${s.no === 1 ? s.list.slice(0, 5).map((c) => `<li class="f t-${c.tk}"><a href="chapter.html">${i("file-code")}${c.dir}</a></li>`).join("") + `<li class="f"><a href="#stage-1">… ${s.list.length - 5}개 더</a></li>` : ""}`).join("")}
</ul></div>`;
const home = page("v3 코드 에디터 · 홈", "dark", css, `${header()}<main class="wrap">
<section class="hero"><div><span class="k">$ cat ROADMAP.md</span><h1>${HERO_T.replace("위한 ", "위한<br class=\"w\"> ")}</h1><p>${HERO_P}</p>
<div class="cta"><a class="btn p" href="chapter.html">${CTA1} ${i("arrow-right")}</a><a class="btn s" href="#lec">${CTA2}</a></div></div>${tree}</section>
<div class="notice"><b>공지</b>${NOTICE}</div>
${whoHtml(i)}
<section class="sec" id="lec"><div class="sec-h"><h2>강의</h2><span class="c">5단계 로드맵 · ${chapters.length}개 챕터</span></div>
<div class="filters">${tracks.map(([l, k, n]) => `<button type="button" class="t-${k}" data-f="${k}" aria-pressed="${k === "all"}">${k === "all" ? "" : "<i></i>"}${l} ${n}</button>`).join("")}</div>
${stages.map((s) => `<section class="stage" id="stage-${s.no}" data-stage><div class="stage-h"><span class="p">${s.no}/</span><b>${s.title}</b><span>${s.from}–${s.to}</span></div><div class="grid">${s.list.map(card).join("")}</div></section>`).join("")}</section>
<section class="sec" id="tips"><div class="sec-h"><h2>꿀팁</h2><span class="c">막혔을 때 꺼내 보는 자료</span></div><div class="tips">${extras.map((e) => `<a class="tip" href="#"><span class="ic">${i("lightbulb")}</span><div><h3>${esc(e.title)}</h3><p>${inline(e.summary.split(", ").slice(0, 3).join(", "))}</p><div class="rel">${e.rel.map((c) => `<span>${c.no} ${esc(c.title.replace(/ \(.+\)$/, ""))}</span>`).join("")}</div></div></a>`).join("")}</div></section>
<section class="sec" id="news"><div class="sec-h"><h2>소식</h2><a class="more" href="#">전체 보기 ${i("chevron-right")}</a></div><div class="log">${news.map((n) => `<a href="#"><time>${n.d}</time><span class="k">${n.k}</span><b>${esc(n.t)}</b></a>`).join("")}</div></section>
</main>${foot}`);
const chapter = page("v3 코드 에디터 · 장 화면", "dark", css, `${header(true, true)}<div class="ide">
<aside class="exp" aria-label="장 목록"><div class="exp-h">${C.dir.toUpperCase()}</div>${parts.map((p, n) => `<details${n < 3 ? " open" : ""}><summary>${i("folder-open")}${esc(p.p)}</summary><ol>${slides.filter((s) => s.n >= p.a && s.n <= p.b).map((s) => `<li><a href="#"${s.n === 1 ? ' aria-current="true"' : ""} title="${esc(s.t)}"><span>${s.n}</span>${esc(s.t)}</a></li>`).join("")}</ol></details>`).join("")}</aside>
<main class="ed t-${C.tk}"><nav class="tabs"><a href="#" aria-current="page">${i("play")}${C.slides}</a><a href="#">${i("file-text")}README.md</a><a href="#">${i("download")}PDF</a></nav>
<div class="ed-in"><div class="ed-h"><div><span class="k">${C.no} · ${C.track} · ${C.group}</span><h1>${esc(C.title)}</h1><p>${inline(C.goal)}</p></div><div class="act"><a class="btn s sm" href="#">${i("external-link")}새 창</a><a class="btn s sm" href="#">${i("download")}PDF 받기</a></div></div>
<div class="player"><iframe src="../../decks/${C.dir}/${C.slides}" title="슬라이드" loading="lazy"></iframe></div>
<div class="keys"><span><kbd>←</kbd> <kbd>→</kbd> 하나씩</span><span><kbd>F</kbd> 전체 화면</span><span><kbd>?</kbd> 단축키</span></div>
<div class="md"><div class="md-h">${i("file-text")}README.md</div><div class="md-b"><h2>학습 목표</h2><ul>${goals.map((g) => `<li>${inline(g)}</li>`).join("")}</ul>
<h2>시작하기 전에</h2><div class="tw"><table><thead><tr><th>할 일</th><th>챕터</th></tr></thead><tbody>${before.map(([a, b]) => `<tr><td>${inline(a)}</td><td>${b}</td></tr>`).join("")}</tbody></table></div></div></div>
<nav class="pn"><a href="#"><small>← 이전</small><b>${prev.no} · ${esc(prev.title)}</b></a><a href="#"><small>다음 →</small><b>${next.no} · ${esc(next.title)}</b></a></nav></div>${foot}</main></div>`);
write("v3", "home.html", home);
write("v3", "chapter.html", chapter);
console.log("v3 done");
