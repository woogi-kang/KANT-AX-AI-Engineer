// 시안 v5 "갤러리": 덱 표지를 썸네일로 크게 써요. 단계마다 옆으로 넘기는 줄. site 폴더에서 node design/v5/gen.mjs
import { i, esc, inline, chapters, byNo, stages, extras, news, NOTICE, C, goals, before, slides, prev, next, page, FOOT, write, LV } from "../lib.mjs";

const cov = (no) => `../shared/covers/${no}.jpg`;
const css = `
:root{--bg:#FFFFFF;--soft:#F4F4F2;--line:#E8E7E3;--ink:#16191F;--sub:#4C5260;--muted:#7C8290;--accent:#2459C9;--accent-soft:#E8EEFB;--theater:#101318;
 --t-term:#4A5262;--t-git:#A0560A;--t-gh:#5A3BB8;--t-py:#1E5FA8;--t-docker:#0D7480;--t-db:#A23B72}
body{background:var(--bg);color:var(--ink);font-size:16px;line-height:1.6}
.t-term{--c:var(--t-term)}.t-git{--c:var(--t-git)}.t-gh{--c:var(--t-gh)}.t-py{--c:var(--t-py)}.t-docker{--c:var(--t-docker)}.t-db{--c:var(--t-db)}
.wrap{max-width:1320px;margin:0 auto;padding:0 32px}
.hd{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.94);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.hd .wrap{height:64px;display:flex;align-items:center;gap:32px}.hd.dark{background:var(--theater);border-color:#22262E;color:#fff}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:17px;letter-spacing:-.025em;white-space:nowrap}
.mark{position:relative;width:30px;height:24px;margin-top:4px;margin-right:5px;overflow:visible;flex:none}.mark i{position:absolute;inset:0;border-radius:5px;background:var(--accent)}.mark i:first-child{transform:translate(5px,-4px);opacity:.35}
.nav{display:flex;gap:24px}.nav a{font-size:15px;font-weight:600;color:var(--muted)}.nav a[aria-current],.nav a:hover{color:inherit}
.hd.dark .nav a{color:#9AA1AE}.hd.dark .nav a[aria-current]{color:#fff}
.hd-r{margin-left:auto;display:flex;gap:4px;align-items:center}
.ib{width:40px;height:40px;border:0;border-radius:50%;background:none;color:inherit;display:grid;place-items:center;cursor:pointer;opacity:.8}.ib:hover{background:rgba(127,127,127,.12);opacity:1}
.om{display:none}
@media (max-width:760px){.nav{display:none}.om{display:grid}}
.intro{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;padding:40px 0 20px;flex-wrap:wrap}
.intro h1{font-size:34px;letter-spacing:-.035em;line-height:1.25;font-weight:800}
.intro p{color:var(--sub);margin-top:6px}
.btn{display:inline-flex;align-items:center;gap:8px;height:46px;padding:0 22px;border-radius:999px;font-weight:700;font-size:15px;white-space:nowrap}
.btn.p{background:var(--ink);color:#fff}.btn.a{background:var(--accent);color:#fff}.btn.s{box-shadow:inset 0 0 0 1px var(--line)}.btn.sm{height:38px;padding:0 16px;font-size:14px}
.feature{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:28px}
.big{position:relative;display:block}.big .bi{position:relative;border-radius:18px;overflow:hidden;background:var(--theater)}
.big img{width:100%;aspect-ratio:16/9;object-fit:cover;transition:transform .5s cubic-bezier(.25,.8,.25,1)}.big:hover img{transform:scale(1.02)}
.big-c{padding:14px 2px 0}.big .tag{position:absolute;left:16px;top:16px;font-size:13px;font-weight:700;background:#fff;color:var(--ink);border-radius:999px;padding:4px 12px}
.big-c h2{font-size:24px;letter-spacing:-.03em}.big-c p{color:var(--sub);margin-top:2px;font-size:15px}
.side-list{display:flex;flex-direction:column;gap:14px}.side-list h3{font-size:14px;color:var(--muted);font-weight:600}
.row-i{display:grid;grid-template-columns:168px minmax(0,1fr);gap:14px;align-items:center}
.row-i img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:10px;background:var(--soft)}
.row-i small{font:600 13px "JetBrains Mono",monospace;color:var(--c)}.row-i b{display:block;font-size:15px;line-height:1.4;letter-spacing:-.02em;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.notice{display:flex;gap:10px;align-items:center;margin-top:28px;padding:12px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);font-size:14px;color:var(--sub)}
.notice b{color:var(--accent);white-space:nowrap}
.shelf{padding-top:48px}
.shelf-h{display:flex;align-items:center;gap:14px;margin-bottom:16px}
.shelf-h h2{font-size:22px;letter-spacing:-.03em;font-weight:800}.shelf-h small{color:var(--muted);font-size:14px}
.shelf-h .nav2{margin-left:auto;display:flex;gap:6px}
.nav2 button{width:36px;height:36px;border-radius:50%;border:0;box-shadow:inset 0 0 0 1px var(--line);background:#fff;display:grid;place-items:center;cursor:pointer}
.nav2 button:hover{box-shadow:inset 0 0 0 1px var(--ink)}
.rail{display:grid;grid-auto-flow:column;grid-auto-columns:calc((100% - 3*20px)/4);gap:20px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding-bottom:4px}
.rail::-webkit-scrollbar{display:none}
.tile{scroll-snap-align:start;display:block;min-width:0}
.tile .im{position:relative;border-radius:12px;overflow:hidden;background:var(--soft);box-shadow:0 0 0 1px var(--line)}
.tile img{width:100%;aspect-ratio:16/9;object-fit:cover;transition:transform .4s cubic-bezier(.25,.8,.25,1)}.tile:hover img{transform:scale(1.04)}
.tile .no{position:absolute;left:10px;top:10px;font:700 12px/1 "JetBrains Mono",monospace;background:#fff;color:var(--c);border-radius:6px;padding:5px 7px}
.tile b{display:block;margin-top:12px;font-size:16px;line-height:1.4;letter-spacing:-.02em;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.tile .m{display:flex;gap:6px;align-items:center;margin-top:4px;font-size:13px;color:var(--muted);min-width:0}
.tile .m em{font-style:normal;color:var(--c);font-weight:600;white-space:nowrap}.tile .m span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.new{margin-left:6px;font-size:12px;font-weight:700;color:#1F8A4C;white-space:nowrap}
.tips{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}
.tip{display:grid;grid-template-columns:200px minmax(0,1fr);gap:18px;align-items:center;padding:14px;border-radius:16px;background:var(--soft)}
.tip img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:10px}.tip small{font-size:13px;color:#B26A00;font-weight:700}.tip h3{font-size:17px;margin-top:2px}.tip p{font-size:14px;color:var(--sub);margin-top:4px}
.newsl{border-top:1px solid var(--ink)}
.newsl a{display:grid;grid-template-columns:120px 90px minmax(0,1fr);gap:16px;padding:16px 0;border-bottom:1px solid var(--line);align-items:baseline}
.newsl time{font:13px "JetBrains Mono",monospace;color:var(--muted)}.newsl .k{font-size:13px;font-weight:700;color:var(--accent)}.newsl b{font-size:16px;letter-spacing:-.02em}
.newsl p{grid-column:3;font-size:14px;color:var(--sub);margin-top:-8px}
.ft{margin-top:72px;background:var(--soft);padding:28px 0 44px;font-size:13px;color:var(--muted)}.ft .wrap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}.ft nav{display:flex;gap:16px}
@media (max-width:1100px){.rail{grid-auto-columns:calc((100% - 2*20px)/3)}}
@media (max-width:900px){.feature{grid-template-columns:1fr}.side-list{display:grid;grid-template-columns:1fr 1fr}.side-list h3{grid-column:1/-1}.row-i{grid-template-columns:1fr;gap:8px}.tips{grid-template-columns:1fr}}
@media (max-width:640px){.wrap{padding:0 16px}.intro{padding:24px 0 16px}.intro h1{font-size:26px}.intro .btn{width:100%;justify-content:center}.big{border-radius:14px}.big-c h2{font-size:19px}.big .bi{border-radius:14px}
 .rail{grid-auto-columns:78%;gap:12px}.shelf-h .nav2{display:none}.shelf{padding-top:36px}.shelf-h h2{font-size:19px}.tile b{font-size:15px}
 .tip{grid-template-columns:1fr}.newsl a{grid-template-columns:1fr;gap:2px}.newsl p{grid-column:1;margin:0}.notice{align-items:flex-start}}
.dlg{position:fixed;inset:0;z-index:50;background:rgba(16,19,24,.5);display:none;justify-content:center;align-items:flex-start;padding:12vh 16px 0}.dlg[open]{display:flex}
.dlg-box{width:min(640px,100%);background:#fff;border-radius:18px;overflow:hidden}
.dlg-in{display:flex;gap:10px;align-items:center;padding:0 20px;height:60px;border-bottom:1px solid var(--line)}.dlg-in input{flex:1;min-width:0;border:0;outline:0;font:inherit;font-size:18px}
.dlg-list{padding:8px;max-height:50vh;overflow:auto}.dlg-item{display:flex;gap:10px;padding:11px 14px;border-radius:10px;font-size:15px}.dlg-item b{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.dlg-item small{color:var(--muted);white-space:nowrap}
.dlg-item.on,.dlg-item:hover{background:var(--soft)}.dlg-empty{padding:20px;text-align:center;color:var(--muted)}
kbd{font-size:12px;color:var(--muted)}
/* 장 화면: 극장 */
.theater{background:var(--theater);padding:20px 0 28px}
.theater .wrap{max-width:1280px}
.player{aspect-ratio:16/9;border-radius:12px;overflow:hidden;background:#000}.player iframe{width:100%;height:100%;border:0}
.strip{display:flex;gap:10px;overflow-x:auto;margin-top:14px;scrollbar-width:none;padding:2px}
.strip a{flex:none;width:150px;position:relative;border-radius:8px;overflow:hidden;opacity:.6;transition:opacity .2s}
.strip a:hover,.strip a[aria-current]{opacity:1}.strip a[aria-current]{box-shadow:0 0 0 2px #6E9BF0}
.strip img{width:100%;aspect-ratio:16/9;object-fit:cover}.strip span{position:absolute;left:6px;bottom:6px;font:700 11px/1 "JetBrains Mono",monospace;background:rgba(0,0,0,.7);color:#fff;border-radius:4px;padding:3px 5px}
.strip .rest{display:grid;place-items:center;background:#1C2028;color:#9AA1AE;font-size:13px;opacity:1}
.head{display:flex;gap:24px;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;padding:28px 0 8px}
.head small{font-size:14px;font-weight:600;color:var(--c)}.head h1{font-size:32px;letter-spacing:-.035em;line-height:1.25;margin-top:4px}.head p{color:var(--sub);margin-top:6px}
.head .act{display:flex;gap:8px}
.cols{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);gap:48px;margin-top:32px}
.cols h2{font-size:18px;letter-spacing:-.02em;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid var(--ink)}
.cols ul{margin:0;padding:0;list-style:none}.cols li{padding:10px 0;border-bottom:1px solid var(--line);font-size:15px;line-height:1.65}
.cols code{font-size:.85em;background:var(--soft);border-radius:4px;padding:1px 5px;white-space:nowrap}.pre code{white-space:normal}
.pre a{display:grid;grid-template-columns:120px minmax(0,1fr);gap:12px;padding:10px 0;border-bottom:1px solid var(--line);align-items:center;font-size:14px}
.pre img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:6px}.pre b{font:700 13px "JetBrains Mono",monospace;margin-right:6px}
.pn{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:48px}.pn a{position:relative;border-radius:14px;overflow:hidden;background:var(--theater);color:#fff}
.pn img{width:100%;aspect-ratio:21/9;object-fit:cover;opacity:.45}.pn div{position:absolute;left:20px;bottom:16px;right:20px}.pn small{color:#C8CDD6;font-size:13px}.pn b{display:block;font-size:17px}
@media (max-width:900px){.cols{grid-template-columns:1fr;gap:32px}}
@media (max-width:640px){.theater{padding:0 0 14px}.theater .wrap{padding:0}.player{border-radius:0}.strip{padding:0 16px}.strip a{width:112px}.head h1{font-size:24px}.head .act{width:100%}.head .act .btn{flex:1;justify-content:center}.pn{grid-template-columns:1fr}.pre a{grid-template-columns:96px minmax(0,1fr)}}
`;
const header = (dark = false) => `<header class="hd${dark ? " dark" : ""}"><div class="wrap"><a class="brand" href="home.html"><span class="mark"><i></i><i></i></span>풀스택 AI/AX 엔지니어</a>
<nav class="nav"><a href="home.html#lec" aria-current="page">강의</a><a href="home.html#tips">꿀팁</a><a href="home.html#news">소식</a></nav>
<div class="hd-r"><button class="ib" type="button" data-search aria-label="강의 찾기 (/)">${i("search")}</button><button class="ib" type="button" aria-label="어둡게 보기">${i("moon")}</button><button class="ib om" type="button" aria-label="메뉴">${i("menu")}</button></div></div></header>`;
const foot = `<footer class="ft"><div class="wrap"><span>${FOOT}</span><nav><a href="#">이용 안내</a><a href="mailto:woogi@memoriz.net">문의</a></nav></div></footer>`;
const tileEl = (c) => `<a class="tile t-${c.tk}" href="chapter.html" data-t="${c.tk}"><div class="im"><img src="${cov(c.no)}" alt="" loading="lazy"><span class="no">${c.no}</span></div><b>${esc(c.title)}${c.no === "46" ? '<span class="new">새 챕터</span>' : ""}</b><div class="m"><em>${c.level}</em><span>· ${esc(c.group)}</span></div></a>`;
const F = byNo["46"];
const home = page("v5 갤러리 · 홈", "light", css, `${header()}<main class="wrap">
<section class="intro"><div><h1>슬라이드를 넘기며 배우는<br>터미널부터 데이터 분석까지</h1><p>${chapters.length}개 챕터, 배우는 순서대로 모았어요.</p></div><a class="btn p" href="chapter.html">01부터 시작하기 ${i("arrow-right")}</a></section>
<section class="feature"><a class="big t-${F.tk}" href="chapter.html"><div class="bi"><img src="${cov(F.no)}" alt=""><span class="tag">새 챕터 · ${F.no}</span></div><div class="big-c"><h2>${esc(F.title)}</h2><p>${esc(F.goal)}</p></div></a>
<div class="side-list"><h3>최근에 올라온 챕터</h3>${["45", "44", "43"].map((n) => byNo[n]).map((c) => `<a class="row-i t-${c.tk}" href="chapter.html"><img src="${cov(c.no)}" alt=""><span><small>${c.no}</small><b>${esc(c.title)}</b></span></a>`).join("")}</div></section>
<div class="notice"><b>공지</b>${NOTICE}</div>
<div id="lec">${stages.map((s) => `<section class="shelf" data-stage><div class="shelf-h"><h2>${s.no}단계 ${s.title}</h2><small>${s.from}–${s.to}</small><div class="nav2"><button type="button" data-scroll="r${s.no}" data-dir="l" aria-label="이전">${i("chevron-left")}</button><button type="button" data-scroll="r${s.no}" aria-label="다음">${i("chevron-right")}</button></div></div><div class="rail" id="r${s.no}">${s.list.map(tileEl).join("")}</div></section>`).join("")}</div>
<section class="shelf" id="tips"><div class="shelf-h"><h2>꿀팁</h2><small>막혔을 때 꺼내 봐요</small></div><div class="tips">${extras.map((e) => `<a class="tip" href="#"><img src="${cov("x-" + e.dir)}" alt=""><div><small>꿀팁</small><h3>${esc(e.title)}</h3><p>${inline(e.summary.split(", ").slice(0, 3).join(", "))}</p></div></a>`).join("")}</div></section>
<section class="shelf" id="news"><div class="shelf-h"><h2>소식</h2><div class="nav2"><a class="btn s sm" href="#">전체 보기</a></div></div><div class="newsl">${news.map((n) => `<a href="#"><time>${n.d}</time><span class="k">${n.k}</span><b>${esc(n.t)}</b><p>${esc(n.p)}</p></a>`).join("")}</div></section>
</main>${foot}`);
const chapter = page("v5 갤러리 · 장 화면", "light", css, `${header(true)}<div class="theater"><div class="wrap"><div class="player"><iframe src="../../decks/${C.dir}/${C.slides}" title="슬라이드" loading="lazy"></iframe></div>
<div class="strip">${Array.from({ length: 12 }, (_, k) => `<a href="#"${k === 0 ? ' aria-current="true"' : ""} title="${esc(slides[k].t)}"><img src="../shared/slides36/${String(k + 1).padStart(2, "0")}.jpg" alt=""><span>${k + 1}</span></a>`).join("")}<a class="rest" href="#">${slides.length - 12}장 더</a></div></div></div>
<main class="wrap t-${C.tk}"><div class="head"><div><small>${C.no} · ${C.stage}단계 ${C.stageTitle} · ${C.group}</small><h1>${esc(C.title)}</h1><p>${inline(C.goal)}</p></div><div class="act"><a class="btn a sm" href="#">${i("download")}PDF 받기</a><a class="btn s sm" href="#">${i("external-link")}새 창</a></div></div>
<div class="cols"><section><h2>이 챕터를 마치면</h2><ul>${goals.map((g) => `<li>${inline(g)}</li>`).join("")}</ul></section>
<section class="pre"><h2>먼저 보고 오면 좋아요</h2>${before.map(([a, b]) => { const n = b.split(",")[0].trim().padStart(2, "0"); return `<a href="#"><img src="${cov(n)}" alt=""><span><b>${b}</b>${inline(a)}</span></a>`; }).join("")}</section></div>
<nav class="pn"><a href="#"><img src="${cov(prev.no)}" alt=""><div><small>이전 챕터</small><b>${prev.no} · ${esc(prev.title)}</b></div></a><a href="#"><img src="${cov(next.no)}" alt=""><div><small>다음 챕터</small><b>${next.no} · ${esc(next.title)}</b></div></a></nav>
</main>${foot}`);
write("v5", "home.html", home);
write("v5", "chapter.html", chapter);
console.log("v5 done");
