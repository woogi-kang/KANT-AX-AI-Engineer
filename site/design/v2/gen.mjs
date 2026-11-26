// 디자인 시안 v2를 만들어요. 레포의 curriculum.json, 챕터 README, 덱 HTML을 읽어서 실제 이름으로 그려요.
// site 폴더에서: node design/v2/gen.mjs
import fs from "node:fs";
import path from "node:path";
import * as si from "simple-icons";
import { HERO_T, HERO_P, CTA1, CTA2, whoHtml, FOOT } from "../lib.mjs";

const HERE = import.meta.dirname;
const SITE = path.resolve(HERE, "../..");
const ROOT = path.resolve(SITE, "..");
const cur = JSON.parse(fs.readFileSync(path.join(ROOT, "curriculum.json"), "utf8"));

/* ── 아이콘: lucide-react의 모양 데이터를 그대로 SVG로 ── */
const lucideCache = {};
async function lu(name) {
  if (!lucideCache[name]) {
    let f = path.join(SITE, "node_modules/lucide-react/dist/esm/icons", name + ".mjs");
    const re = /from .\.\/(.+?)\.mjs/.exec(fs.readFileSync(f, "utf8"));
    if (!fs.readFileSync(f, "utf8").includes("__iconData") && re) f = path.join(path.dirname(f), re[1] + ".mjs");
    const mod = await import(f);
    lucideCache[name] = mod.__iconData.node.map(([t, a]) => `<${t} ${Object.entries(a).filter(([k]) => k !== "key").map(([k, v]) => `${k}="${v}"`).join(" ")}/>`).join("");
  }
  return lucideCache[name];
}
const ICONS = ["search","sun","moon","menu","arrow-right","chevron-right","chevron-left","download","external-link","panel-left","lightbulb","x","square-terminal","database","copy","info","triangle-alert","circle-x","corner-down-left","arrow-up-down","keyboard","user","building-2","users","circle-check"];
const IC = {};
for (const n of ICONS) IC[n] = await lu(n);
const i = (n, cls = "i") => `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true">${IC[n]}</svg>`;

/* ── 로고: Simple Icons(CC0), 없는 것은 Lucide 선 아이콘 ── */
const brand = (x) => ({ title: x.title, hex: "#" + x.hex, path: x.path });
const LOGO = {
  terminal: { title: "터미널", hex: "#3F4757", lucide: "square-terminal" },
  database: { title: "데이터베이스", hex: "#A23B72", lucide: "database" },
  git: brand(si.siGit), github: brand(si.siGithub), uv: brand(si.siUv), jupyter: brand(si.siJupyter),
  python: brand(si.siPython), docker: brand(si.siDocker), nginx: brand(si.siNginx), mysql: brand(si.siMysql),
  postgresql: brand(si.siPostgresql), numpy: brand(si.siNumpy), pandas: brand(si.siPandas),
};
const BY_CH = { "01": "terminal", "09": "uv", "10": "jupyter", "11": "github", "31": "nginx", "32": "database", "33": "mysql", "34": "postgresql", "44": "python", "45": "numpy", "46": "pandas" };
const BY_TRACK = { 터미널: "terminal", Git: "git", GitHub: "github", 파이썬: "python", Docker: "docker", 데이터베이스: "postgresql" };
const SECOND = { "06": "github", "31": "docker", "33": "docker", "34": "docker", "44": "postgresql", "45": "pandas" };
const TK = { 터미널: "term", Git: "git", GitHub: "gh", 파이썬: "py", Docker: "docker", 데이터베이스: "db" };
const LV = { 입문: 1, 기초: 2, 응용: 3 };
const tile = (k, sz = 36) => {
  const L = LOGO[k];
  const g = L.lucide ? `<svg viewBox="0 0 24 24" class="lu" style="color:${L.hex}">${IC[L.lucide]}</svg>` : `<svg viewBox="0 0 24 24" fill="${L.hex}"><path d="${L.path}"/></svg>`;
  return `<span class="logo-tile" style="--sz:${sz}px" title="${L.title}">${g}</span>`;
};
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const inline = (s) => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>");
const plain = (s) => s.replace(/`/g, "");

/* ── 데이터 ── */
const chapters = cur.chapters.map((c) => {
  const no = c.dir.slice(0, 2);
  const a = BY_CH[no] ?? BY_TRACK[c.track];
  const b = SECOND[no];
  return { ...c, no, tk: TK[c.track], logos: b ? [a, b] : [a] };
});
const byNo = Object.fromEntries(chapters.map((c) => [c.no, c]));
const stages = cur.stages.map((s, si_) => {
  const groups = s.groups.map((g) => ({ ...g, chapters: chapters.filter((c) => c.no >= g.from && c.no <= g.to) }));
  groups.forEach((g) => g.chapters.forEach((c) => { c.group = g.title; c.stage = si_ + 1; c.stageTitle = s.title; }));
  const list = groups.flatMap((g) => g.chapters);
  const logos = [...new Set(list.map((c) => c.logos[0]))];
  return { ...s, no: si_ + 1, groups, list, logos, from: list[0].no, to: list.at(-1).no };
});
const NEWEST = new Set(["46"]); // 시안에서는 맨 마지막 챕터만 새 챕터로 보여 줘요

/* ── 조각 ── */
const markSvg = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 19h5v-5h5V9h6"/></svg>`;
const brandEl = (href = "home.html") => `<a class="brand" href="${href}"><span class="brand-mark">${markSvg}</span><span>풀스택 AI/AX <small>엔지니어</small></span></a>`;
const lvl = (l) => `<span class="lvl" data-l="${LV[l]}"><i><b></b><b></b><b></b></i>${l}</span>`;
const thumb = (c) => `<div class="thumb t-${c.tk}" aria-hidden="true"><span class="no">${c.no}</span><span class="logos">${c.logos.map((k) => tile(k, 34)).join("")}</span><span class="line"><code>${esc(c.keyword)}</code></span></div>`;
const card = (c) => `<a class="card" href="chapter.html" data-t="${c.tk}">${thumb(c)}<div class="card-b"><h3>${esc(c.title)}${NEWEST.has(c.no) ? '<span class="tag-new">새 챕터</span>' : ""}</h3><div class="card-m">${lvl(c.level)}<span class="dot"></span><span class="grp">${esc(c.group)}</span></div></div></a>`;

const header = (cur_ = "강의", full = false, withNavBtn = false) => `<header class="hd${full ? " full" : ""}"><div class="wrap">
  ${withNavBtn ? `<button class="icon-btn" type="button" data-nav-toggle aria-label="목차 접기">${i("panel-left")}</button>` : ""}
  ${brandEl()}
  <nav class="nav" aria-label="메뉴">${["강의", "꿀팁", "소식"].map((n) => `<a href="home.html#${{ 강의: "lectures", 꿀팁: "tips", 소식: "news" }[n]}"${n === cur_ ? ' aria-current="page"' : ""}>${n}</a>`).join("")}</nav>
  <div class="hd-r">
    <button class="search-btn" type="button" data-search>${i("search")}<span class="lbl">강의 찾기</span><kbd>/</kbd></button>
    <button class="icon-btn" type="button" data-theme-toggle aria-label="어둡게 보기">${i("moon")}</button>
    <button class="icon-btn only-m" type="button" aria-label="메뉴">${i("menu")}</button>
  </div>
</div></header>`;

const footer = `<footer class="ft"><div class="wrap">
  <span>${FOOT}</span>
  <nav><a href="#">이용 안내</a><a href="mailto:woogi@memoriz.net">문의</a><a href="#">GitHub</a></nav>
</div></footer>`;

const searchData = JSON.stringify([
  ...chapters.map((c) => ({ t: `${c.no} · ${c.title}`, s: c.track, k: c.keyword })),
  ...cur.extras.map((e) => ({ t: e.title, s: "꿀팁", k: "" })),
]);
const searchDlg = `<div class="dlg" data-dlg role="dialog" aria-modal="true" aria-label="강의 찾기"><div class="dlg-box">
  <div class="dlg-in">${i("search")}<input type="text" placeholder="챕터 이름, 명령어로 찾아요 (예: JOIN, git diff)" aria-label="찾을 말"><kbd>Esc</kbd></div>
  <div class="dlg-list" role="listbox"></div>
  <div class="dlg-foot"><span>${i("arrow-up-down", "i")}고르기</span><span>${i("corner-down-left", "i")}열기</span><span><kbd>Ctrl</kbd><kbd>K</kbd> 어디서나 열기</span></div>
</div></div>`;
const script = `<script>
(()=>{const d=document.documentElement;try{const t=localStorage.getItem('ds2-theme');if(t)d.dataset.theme=t}catch(e){}
document.querySelectorAll('[data-theme-toggle]').forEach(b=>b.onclick=()=>{const n=d.dataset.theme==='dark'?'light':'dark';d.dataset.theme=n;try{localStorage.setItem('ds2-theme',n)}catch(e){}});
document.querySelectorAll('[data-nav-toggle]').forEach(b=>b.onclick=()=>{const s=document.querySelector('.shell');s.dataset.nav=s.dataset.nav==='closed'?'open':'closed'});
const dlg=document.querySelector('[data-dlg]');if(!dlg)return;const inp=dlg.querySelector('input'),list=dlg.querySelector('.dlg-list');const data=${searchData};let sel=0,items=[];
function draw(){const q=inp.value.trim().toLowerCase();items=data.filter(x=>!q||(x.t+' '+x.k).toLowerCase().includes(q)).slice(0,8);sel=Math.min(sel,Math.max(items.length-1,0));
list.innerHTML=items.length?items.map((x,j)=>'<a class="dlg-item" href="chapter.html" role="option" aria-selected="'+(j===sel)+'"><b>'+x.t.replace(/</g,'&lt;')+'</b><small>'+x.s+'</small></a>').join(''):'<p style="padding:24px;text-align:center;color:var(--muted);font-size:14px">찾는 챕터가 없어요. 다른 말로 찾아봐요.</p>'}
function open(){dlg.setAttribute('open','');inp.value='';sel=0;draw();inp.focus()}function close(){dlg.removeAttribute('open')}
document.querySelectorAll('[data-search]').forEach(b=>b.onclick=open);inp.oninput=()=>{sel=0;draw()};dlg.onclick=e=>{if(e.target===dlg)close()};
addEventListener('keydown',e=>{const t=e.target.tagName;if(!dlg.hasAttribute('open')){if((e.key==='/'&&t!=='INPUT'&&t!=='TEXTAREA')||((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k')){e.preventDefault();open()}return}
if(e.key==='Escape')close();if(e.key==='ArrowDown'){sel=Math.min(sel+1,items.length-1);draw();e.preventDefault()}if(e.key==='ArrowUp'){sel=Math.max(sel-1,0);draw();e.preventDefault()}});
const tabs=document.querySelectorAll('.tab[data-f]');tabs.forEach(b=>b.onclick=()=>{tabs.forEach(x=>x.setAttribute('aria-pressed',x===b));const f=b.dataset.f;document.querySelectorAll('.card[data-t]').forEach(c=>c.hidden=f!=='all'&&c.dataset.t!==f);document.querySelectorAll('.stage').forEach(s=>s.hidden=!s.querySelector('.card:not([hidden])'))});
const nb=document.querySelector('[data-notice-close]');if(nb)nb.onclick=()=>nb.closest('.notice').remove();})();
</script>`;
const page = (title, body, extraCss = "") => `<!doctype html><html lang="ko" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${title}</title><link rel="preload" href="fonts/PretendardVariable.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="ds.css">${extraCss ? `<style>${extraCss}</style>` : ""}</head>
<body>${body}${searchDlg}${script}</body></html>`;

/* ── 화면 1: 홈 ── */
const roadmap = `<ol class="road" aria-label="다섯 단계">${stages.map((s) => `<li style="--h:${s.no}"><a href="#stage-${s.no}"><span class="road-n">${s.no}단계</span><b>${s.title}</b><span class="road-l">${s.logos.slice(0, 3).map((k) => tile(k, 28)).join("")}</span><small>${s.from}–${s.to}</small></a></li>`).join("")}</ol>`;
const trackCounts = Object.entries(TK).map(([label, k]) => ({ label, k, n: chapters.filter((c) => c.tk === k).length }));
const news = [
  ...cur.updates.slice(-2).reverse().map((u) => ({ k: "업데이트", d: u.date, t: u.title, p: plain(u.summary) })),
];
news.unshift({ k: "새 챕터", d: "2026-11-24", t: "46 · " + byNo["46"].title, p: plain(byNo["46"].goal) });
const homeCss = `
@media (max-width:640px){br.w{display:none}}
.who{margin-top:var(--s-7);padding:var(--s-6);background:var(--surface);border:1px solid var(--line);border-radius:var(--r-lg)}
.who-h{display:flex;gap:var(--s-5);align-items:baseline;flex-wrap:wrap}.who-h h2{font-size:var(--fs-20);font-weight:800}.who-h p{color:var(--sub);font-size:var(--fs-14)}
.who-g{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--s-5);margin-top:var(--s-5)}
.who-i .i{width:22px;height:22px;color:var(--accent)}.who-i b{display:block;margin-top:var(--s-2);font-size:var(--fs-16)}.who-i p{font-size:var(--fs-14);color:var(--sub);margin-top:2px}
.pr{list-style:none;margin:var(--s-5) 0 0;padding:var(--s-4) 0 0;border-top:1px solid var(--line);display:flex;flex-wrap:wrap;gap:var(--s-2) var(--s-5);font-size:var(--fs-14);color:var(--sub)}
.pr li{display:flex;gap:6px;align-items:center}.pr .i{width:16px;height:16px;color:var(--run)}
@media (max-width:760px){.who{padding:var(--s-5)}.who-g{grid-template-columns:1fr;gap:var(--s-4)}}

.hero{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,560px);gap:var(--s-7);align-items:end;padding:var(--s-8) 0 var(--s-6)}
.hero h1{font-size:36px;line-height:1.3;font-weight:800;letter-spacing:-.035em}
.hero p{margin-top:var(--s-4);font-size:var(--fs-18);color:var(--sub);max-width:30em}
.hero-cta{display:flex;gap:var(--s-3);margin-top:var(--s-6);flex-wrap:wrap}
.road{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(5,1fr);gap:8px;align-items:end}
.road li{height:calc(110px + var(--h) * 34px)}
.road a{height:100%;display:flex;flex-direction:column;gap:6px;padding:12px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r-md);transition:border-color var(--dur-ui),transform var(--dur-ui) var(--ease-arrive)}
.road a:hover{border-color:var(--accent);transform:translateY(-2px)}
.road-n{font-size:var(--fs-12);font-weight:700;line-height:1;color:var(--accent)}
.road b{font-size:var(--fs-14);line-height:1.35;letter-spacing:-.02em}
.road-l{display:flex;gap:4px;margin-top:auto;flex-wrap:wrap}
.road small{font:500 var(--fs-12)/1 var(--font-mono);color:var(--faint)}
.lec-bar{position:sticky;top:var(--header-h);z-index:5;background:var(--paper);padding:var(--s-3) 0;box-shadow:0 0 0 0 var(--paper)}
@media (max-width:1040px){.hero{grid-template-columns:1fr;align-items:start}.road{max-width:560px}}
@media (max-width:640px){.hero{padding:var(--s-6) 0 var(--s-5);gap:var(--s-6)}.hero h1{font-size:28px}.hero p{font-size:var(--fs-16)}.hero-cta .btn{flex:1}
 .road{grid-template-columns:1fr;gap:6px}.road li{height:auto}.road a{flex-direction:row;align-items:center;gap:10px;padding:10px 12px}.road b{flex:1;min-width:0}.road-l{margin:0;flex-wrap:nowrap}.road small{display:none}
 .cards{grid-template-columns:1fr 1fr;gap:var(--s-3)}.card-b{padding:var(--s-3)}.card-b h3{font-size:var(--fs-14)}.thumb .no{font-size:20px;left:10px;top:9px}.thumb .logos{right:8px;top:8px}.thumb .logo-tile{--sz:26px!important}.thumb .line{left:10px;right:10px;bottom:10px}.thumb .line code{font-size:11px;padding:6px 7px}.card-m .dot,.card-m .grp{display:none}
 .sec{padding-top:var(--s-7)}}
@media (max-width:360px){.cards{grid-template-columns:1fr}}
`;
const home = page("강의 · 풀스택 AI/AX 엔지니어", `${header("강의")}
<main class="wrap" id="main">
  <section class="hero">
    <div>
      <h1>${HERO_T.replace("위한 ", "위한<br class=\"w\"> ")}</h1>
      <p>${HERO_P}</p>
      <div class="hero-cta"><a class="btn primary" href="chapter.html">${CTA1} ${i("arrow-right")}</a><a class="btn secondary" href="#lectures">${CTA2}</a></div>
    </div>
    ${roadmap}
  </section>
  <div class="notice" role="status"><span class="k">공지</span><p>12월 수업부터 머신러닝 챕터가 이어서 올라와요. 슬라이드 아래 PDF 받기로 미리 내려받을 수 있어요.</p><button class="icon-btn" type="button" data-notice-close aria-label="공지 닫기">${i("x")}</button></div>
  ${whoHtml(i)}

  <section class="sec" id="lectures">
    <div class="sec-h"><div><h2>강의</h2><p>다섯 단계로 나눈 로드맵이에요. ${chapters.length}개 챕터를 배우는 순서대로 놓았어요.</p></div></div>
    <div class="lec-bar"><div class="tabs" role="group" aria-label="분류로 걸러 보기">
      <button class="tab" type="button" data-f="all" aria-pressed="true">전체 <small>${chapters.length}</small></button>
      ${trackCounts.map((t) => `<button class="tab t-${t.k}" type="button" data-f="${t.k}" aria-pressed="false"><span class="sw"></span>${t.label} <small>${t.n}</small></button>`).join("")}
    </div></div>
    ${stages.map((s) => `<section class="stage" id="stage-${s.no}">
      <header class="stage-h"><span class="n">${s.no}단계</span><h3>${s.title}</h3><small>${s.from}–${s.to}</small><p>${esc(s.summary)}</p></header>
      <div class="cards">${s.list.map(card).join("")}</div>
    </section>`).join("")}
  </section>

  <section class="sec" id="tips">
    <div class="sec-h"><div><h2>꿀팁</h2><p>순서와 상관없이 막혔을 때 꺼내 봐요</p></div></div>
    <div class="tips">${cur.extras.map((e) => `<a class="tip" href="#"><span class="tip-ic">${i("lightbulb")}</span><div><h3>${esc(e.title)}</h3><p>${inline(e.summary.split(", ").slice(0, 3).join(", "))}</p><div class="rel">${e.related.map((d) => byNo[d.slice(0, 2)]).map((c) => `<span class="rel-i" style="display:inline-flex;gap:6px;align-items:center;height:26px;padding:0 8px;border-radius:6px;background:var(--sunken);font-size:12px;color:var(--sub)"><b style="font-family:var(--font-mono);color:var(--ink)">${c.no}</b>${esc(c.title.replace(/ \(.+\)$/, ""))}</span>`).join("")}</div></div></a>`).join("")}
    </div>
  </section>

  <section class="sec" id="news">
    <div class="sec-h"><div><h2>소식</h2><p>새 챕터와 바뀐 점을 알려 드려요</p></div><a class="more" href="#">전체 보기 ${i("chevron-right", "i")}</a></div>
    <div class="news">${news.map((n) => `<a class="news-i" href="#"><span class="k"><b>${n.k}</b>${n.d.replace(/-/g, ".")}</span><h3>${esc(n.t)}</h3><p>${esc(n.p)}</p></a>`).join("")}</div>
  </section>
</main>
${footer}`, homeCss);

/* ── 화면 2: 장 화면 (36) ── */
const C = byNo["36"];
const readme = fs.readFileSync(path.join(ROOT, C.dir, "README.md"), "utf8");
const sect = (name) => (readme.split(/^## /m).find((x) => x.startsWith(name)) ?? "").split("\n").slice(1).join("\n").trim();
const goals = sect("학습 목표").split("\n").filter((l) => l.startsWith("- ")).map((l) => `<li>${inline(l.slice(2))}</li>`).join("");
const tableRows = (md) => md.split("\n").filter((l) => l.startsWith("|")).slice(2).map((l) => l.split("|").slice(1, -1).map((x) => x.trim()));
const before = tableRows(sect("시작하기 전에"));
const parts = tableRows(sect("구성")).map(([p, range]) => { const [a, b] = range.split(/[–-]/).map(Number); return { p, a, b: b || a }; });
const deckHtml = fs.readFileSync(path.join(ROOT, C.dir, C.slides), "utf8");
const strip = (h) => h.replace(/<br\s*\/?>/gi, " ").replace(/<[^>]+>/g, "").replace(/&nbsp;/g, " ").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();
const slides = [...deckHtml.matchAll(/<section\b([^>]*)>([\s\S]*?)<\/section>/g)].map((m, n) => {
  const body = m[2].replace(/<aside\b[\s\S]*?<\/aside>/g, "");
  const h = /<h([1-3])\b[^>]*>([\s\S]*?)<\/h\1>/.exec(body);
  return { n: n + 1, t: h ? strip(h[2]) : `${n + 1}쪽` };
});
const side = parts.map((p) => `<div class="side-part">${esc(p.p)}</div><ol>${slides.filter((s) => s.n >= p.a && s.n <= p.b).map((s) => `<li><a href="#"${s.n === 1 ? ' aria-current="true"' : ""} title="${esc(s.t)}"><span>${s.n}</span>${esc(s.t.length > 26 ? s.t.slice(0, 25) + "…" : s.t)}</a></li>`).join("")}</ol>`).join("");
const prev = byNo["35"], next = byNo["37"];
const chCss = `
.ch{max-width:1040px;margin:0 auto;padding:var(--s-6) var(--gutter) 0}
.ch-h{display:flex;gap:var(--s-5);align-items:flex-start;margin:var(--s-4) 0 var(--s-5)}
.ch-h .thumb{width:176px;flex:none;border-radius:var(--r-md);border:1px solid var(--line)}
.ch-h .thumb .no{font-size:18px;left:10px;top:8px}.ch-h .thumb .logos{right:8px;top:8px}.ch-h .thumb .logo-tile{--sz:24px!important}.ch-h .thumb .line{left:10px;right:10px;bottom:10px}.ch-h .thumb .line code{font-size:12px;padding:6px 8px}
.ch-h h1{font-size:var(--fs-32);font-weight:800;letter-spacing:-.03em;line-height:1.25}
.ch-h p{color:var(--sub);margin-top:6px}
.ch-meta{display:flex;align-items:center;gap:var(--s-3);flex-wrap:wrap;margin-top:var(--s-3);font-size:var(--fs-13);color:var(--muted)}
.ch-meta .trk{color:var(--c);font-weight:600}
.ch-act{display:flex;gap:var(--s-2);margin-left:auto}
.ch-body{display:grid;grid-template-columns:minmax(0,1fr) 200px;gap:var(--s-7);margin-top:var(--s-6)}
.toc{position:sticky;top:calc(var(--header-h) + 24px);align-self:start;font-size:var(--fs-13)}
.toc b{display:block;color:var(--muted);font-size:var(--fs-12);margin-bottom:var(--s-2)}
.toc a{display:block;padding:4px 0 4px 12px;border-left:2px solid var(--line);color:var(--sub)}
.toc a[aria-current]{border-color:var(--accent);color:var(--accent);font-weight:600}
@media (max-width:1180px){.ch-body{grid-template-columns:minmax(0,1fr)}.toc{display:none}}
@media (max-width:640px){.ch{padding-top:var(--s-4)}.ch-h{flex-direction:column;gap:var(--s-3)}.ch-h .thumb{display:none}.ch-h h1{font-size:var(--fs-24)}.ch-act{margin-left:0;width:100%}.ch-act .btn{flex:1}.player{border-radius:var(--r-md)}.player-foot{display:none}}
`;
const chapterPage = page(`${C.no} ${C.title} · 풀스택 AI/AX 엔지니어`, `${header("강의", true, true)}
<div class="shell" data-nav="open">
  <aside class="side" aria-label="장 목록"><div class="side-h"><small>${C.no} · ${C.track}</small><b>${esc(C.title)}</b></div>${side}</aside>
  <main class="ch t-${C.tk}" id="main">
    <nav class="crumb" aria-label="위치"><a href="home.html#lectures">강의</a>${i("chevron-right")}<a href="home.html#stage-${C.stage}">${C.stage}단계 ${C.stageTitle}</a>${i("chevron-right")}<span>${C.group}</span></nav>
    <header class="ch-h">${thumb(C)}<div style="flex:1;min-width:0">
      <h1>${esc(C.title)}</h1><p>${inline(C.goal)}</p>
      <div class="ch-meta"><span class="trk">${C.no} · ${C.track}</span>${lvl(C.level)}<div class="ch-act"><a class="btn secondary sm" href="#">${i("external-link")}새 창으로 보기</a><a class="btn secondary sm" href="#">${i("download")}PDF 받기</a></div></div>
    </div></header>
    <div class="player"><iframe src="../../decks/${C.dir}/${C.slides}" title="${esc(C.title)} 슬라이드" loading="lazy"></iframe></div>
    <div class="player-foot"><span><kbd>←</kbd><kbd>→</kbd> 애니메이션 하나씩</span><span><kbd>F</kbd> 전체 화면</span><span><kbd>?</kbd> 단축키</span><span style="margin-left:auto">${slides.length}장</span></div>
    <div class="ch-body">
      <article class="prose">
        <h2 id="goal">학습 목표</h2><ul>${goals}</ul>
        <h2 id="before">시작하기 전에</h2>
        <div class="tablewrap"><table><thead><tr><th>할 일</th><th>챕터</th></tr></thead><tbody>${before.map(([a, b]) => `<tr><td>${inline(a)}</td><td>${b}</td></tr>`).join("")}</tbody></table></div>
        <h2 id="try">실습 미리 보기</h2>
        <div class="code term"><button class="copy" type="button" aria-label="복사">${i("copy")}</button><span class="d">$</span> docker exec -it my-pg psql -U postgres -d kant_shop
<span class="p">kant_shop=#</span> SELECT name, price FROM product WHERE price &gt;= 30000;</div>
        <div class="callout" style="margin-top:16px">${i("info")}<div>실습 칸이 생기면 이 자리에서 바로 쳐 보고, 수업 출력과 나란히 비교해요.</div></div>
      </article>
      <nav class="toc" aria-label="이 챕터에서"><b>이 챕터에서</b><a href="#goal" aria-current="true">학습 목표</a><a href="#before">시작하기 전에</a><a href="#">구성</a><a href="#try">실습</a><a href="#">명령어 요약</a><a href="#">문제 해결</a></nav>
    </div>
    <nav class="pn" aria-label="이전, 다음 챕터"><a href="#"><small>이전 챕터</small><b>${prev.no} · ${esc(prev.title)}</b></a><a href="#"><small>다음 챕터</small><b>${next.no} · ${esc(next.title)}</b></a></nav>
    ${footer.replace('class="ft"', 'class="ft" style="margin-left:calc(var(--gutter)*-1);margin-right:calc(var(--gutter)*-1)"')}
  </main>
</div>`, chCss);

fs.writeFileSync(path.join(HERE, "home.html"), home);
fs.writeFileSync(path.join(HERE, "chapter.html"), chapterPage);

/* ── 시안 문서 (index.html) ── */
const sw = (name, v, note = "") => `<div class="swatch"><span style="background:var(${v})"></span><b>${name}</b><code>${v}</code>${note ? `<small>${note}</small>` : ""}</div>`;
const docCss = `
.doc{max-width:1120px;margin:0 auto;padding:var(--s-7) var(--gutter) 0}
.doc>header h1{font-size:var(--fs-32);font-weight:800;letter-spacing:-.03em}
.doc>header p{color:var(--sub);margin-top:var(--s-2);max-width:44em}
.doc-nav{display:flex;flex-wrap:wrap;gap:6px;margin-top:var(--s-5)}
.doc-nav a{height:32px;display:inline-flex;align-items:center;padding:0 12px;border:1px solid var(--line);border-radius:999px;font-size:var(--fs-13);background:var(--surface)}
.doc section{padding-top:var(--s-8);scroll-margin-top:var(--header-h)}
.doc h2{font-size:var(--fs-24);font-weight:800;letter-spacing:-.025em}
.doc h2+p{color:var(--sub);margin-top:6px;max-width:46em}
.doc h3{font-size:var(--fs-16);font-weight:700;margin:var(--s-6) 0 var(--s-3)}
.grid{display:grid;gap:var(--s-4)}
.g2{grid-template-columns:repeat(2,minmax(0,1fr))}.g3{grid-template-columns:repeat(3,minmax(0,1fr))}.g4{grid-template-columns:repeat(4,minmax(0,1fr))}
@media (max-width:800px){.g2,.g3,.g4{grid-template-columns:minmax(0,1fr)}}
.box{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-lg);padding:var(--s-5)}
.box h4{font-size:var(--fs-14);font-weight:700;margin-bottom:6px}
.box p{font-size:var(--fs-14);color:var(--sub)}
.broke{display:grid;grid-template-columns:minmax(0,320px) minmax(0,1fr);gap:var(--s-5);align-items:start}
.broke img{width:100%;border-radius:var(--r-md);border:1px solid var(--line)}
.broke b{display:block;font-size:var(--fs-16);margin-bottom:4px}
.broke p{font-size:var(--fs-14);color:var(--sub)}
.broke .fix{margin-top:var(--s-2);font-size:var(--fs-14);color:var(--run)}
@media (max-width:700px){.broke{grid-template-columns:1fr}}
.swatches{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:var(--s-3)}
.swatch{display:flex;flex-direction:column;gap:2px;font-size:var(--fs-13)}
.swatch span{height:48px;border-radius:var(--r-md);border:1px solid var(--line);margin-bottom:6px}
.swatch code{color:var(--muted);font-size:var(--fs-12)}
.swatch small{color:var(--muted);font-size:var(--fs-12)}
.scale{display:flex;flex-direction:column;gap:var(--s-2)}
.scale div{display:flex;align-items:baseline;gap:var(--s-4);border-bottom:1px solid var(--line);padding-bottom:var(--s-2);overflow:hidden}
.scale code{width:120px;flex:none;color:var(--muted);font-size:var(--fs-12)}
.scale span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.space{display:flex;flex-direction:column;gap:6px}
.space div{display:flex;align-items:center;gap:var(--s-3);font-size:var(--fs-12)}
.space i{height:12px;background:var(--accent);border-radius:2px}
.row{display:flex;flex-wrap:wrap;gap:var(--s-3);align-items:center}
.label{display:block;font:500 var(--fs-12)/1.4 var(--font-mono);color:var(--muted);margin-top:var(--s-2)}
.anat{position:relative;max-width:420px}
.anat .pin{position:absolute;display:flex;align-items:center;gap:6px;font-size:var(--fs-12);color:var(--ink);font-weight:600;white-space:nowrap}
.anat .pin i{width:20px;height:20px;border-radius:50%;background:var(--ink);color:var(--paper);display:grid;place-items:center;font-style:normal;font-size:11px}
.legend{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:var(--s-3);font-size:var(--fs-14);color:var(--sub)}
.legend b{display:inline-grid;place-items:center;width:20px;height:20px;border-radius:50%;background:var(--ink);color:var(--paper);font-size:11px;margin-right:8px}
.screens{display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:var(--s-5);align-items:start}
.screens a.shot{display:block;border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden;background:var(--surface)}
.screens a.shot img{width:100%}
.screens a.shot span{display:flex;justify-content:space-between;padding:10px 14px;font-size:var(--fs-13);font-weight:600;border-top:1px solid var(--line)}
@media (max-width:800px){.screens{grid-template-columns:1fr}}
.cmp{width:100%;border-collapse:collapse;font-size:var(--fs-14);background:var(--surface);border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden}
.cmp th,.cmp td{padding:12px 14px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.cmp th{background:var(--sunken);font-size:var(--fs-13);color:var(--sub)}
.tablewrap{overflow-x:auto}
`;
const sample = byNo["17"];
const doc = page("디자인 시스템 v2 · 풀스택 AI/AX 엔지니어", `${header("")}
<main class="doc" id="main">
  <header><h1>학습 사이트 디자인 시스템 v2</h1>
  <p>카드와 썸네일로 보기 좋게 바꾸면서 흐트러진 규칙을 처음부터 다시 정했어요. 덱의 종이색과 파랑 하나를 바탕에 두고, 그림은 그 챕터에서 배우는 코드 한 줄로 그려요.</p>
  <nav class="doc-nav"><a href="#broke">무너진 곳</a><a href="#rules">원칙</a><a href="#tokens">토큰</a><a href="#brand">로고와 아이콘</a><a href="#thumb">썸네일</a><a href="#comp">컴포넌트</a><a href="#screens">화면</a><a href="home.html">홈 화면 열기</a><a href="chapter.html">장 화면 열기</a></nav></header>

  <section id="broke"><h2>지금 화면에서 무너진 곳</h2><p>토큰 파일은 그대로 있는데, 카드형으로 바꾸면서 화면이 토큰을 거치지 않고 브랜드 색과 새 장식을 직접 썼어요.</p>
    <div class="grid" style="margin-top:24px;gap:32px">
      <div class="broke"><img src="img/broke-hero.png" alt="지금 홈의 어두운 히어로"><div><b>1. 바탕이 두 개가 됐어요</b><p>시안은 덱과 같은 종이색(#F6F5F1)인데, 홈은 흰 바탕에 짙은 남색 그라데이션 히어로를 얹었어요. 반짝이 아이콘 배지, 숫자 통계, 로고 구름도 이 화면에만 있는 장식이에요.</p><p class="fix">고친 방법: 바탕은 종이색 하나. 히어로 그림은 장식 대신 다섯 단계를 계단으로 그려서 배우는 순서를 보여 줘요.</p></div></div>
      <div class="broke"><img src="img/broke-cards.png" alt="지금 카드 썸네일"><div><b>2. 색이 분류 6색에서 브랜드 13색으로 늘었어요</b><p>썸네일 바탕을 로고 원래 색(Git 빨강, uv 자주, Jupyter 주황)으로 칠해서, 분류색 6개와 강조색 파랑 규칙이 사라졌어요. 파이썬 17장은 같은 파란 칸에 같은 로고라 서로 구별되지 않아요.</p><p class="fix">고친 방법: 바탕은 분류색의 옅은 색. 로고는 흰 타일 안에 작게. 챕터마다 다른 것은 그 장의 코드 한 줄이에요.</p></div></div>
      <div class="broke"><img src="img/broke-meta.png" alt="지금 카드 아래 표시"><div><b>3. 카드 한 장에 표시가 다섯 개예요</b><p>번호, 오른쪽 위 묶음 이름, 키워드, NEW, 레벨 막대, 분류 배지가 한꺼번에 붙어요. NEW는 46개 챕터 모두에 붙었는데, Cloudflare가 기록을 얕게 받아서 모든 README의 첫 날짜가 오늘로 잡힌 탓이에요.</p><p class="fix">고친 방법: 카드에는 그림, 제목, 한 줄(레벨 · 묶음)만. 새 챕터 표시는 날짜를 curriculum.json에 적어 두고 7일 안의 것만.</p></div></div>
      <div class="broke"><img src="img/broke-side.png" alt="지금 홈의 사이드바"><div><b>4. 틀이 화면마다 달라요</b><p>홈에 장 화면용 사이드바가 붙어 있고, 흰 사이드바가 화면 중간에서 끊겨요. 메뉴 이름(강의, 꿀팁, 소식)은 바꿨지만 장 화면 위치 표시는 아직 "학습 로드맵"이에요.</p><p class="fix">고친 방법: 홈, 꿀팁, 소식은 위 메뉴만. 사이드바는 장 화면에만 두고 파트별로 묶어요.</p></div></div>
    </div>
  </section>

  <section id="rules"><h2>원칙 네 가지</h2><p>새 화면이나 컴포넌트를 만들 때 이 넷으로 먼저 걸러요.</p>
    <div class="grid g2" style="margin-top:24px">
      <div class="box"><h4>색은 뜻이 있을 때만</h4><p>강조는 파랑 하나. 분류색 6개는 썸네일 바탕과 분류 글자에만, 초록·빨강·주황은 실행, 오류, 확인에만 써요. 그라데이션은 쓰지 않아요.</p></div>
      <div class="box"><h4>카드에는 세 가지만</h4><p>그림, 제목, 한 줄. 한 줄은 레벨과 묶음 이름이에요. 수강료, 숫자 통계, 의미 없는 배지는 넣지 않아요.</p></div>
      <div class="box"><h4>그림은 그 챕터의 내용으로</h4><p>썸네일 가운데는 그 장에서 처음 치는 코드 한 줄(curriculum.json의 keyword)이에요. 로고는 무슨 도구인지 알려 주는 표시로만 작게 둬요.</p></div>
      <div class="box"><h4>값은 토큰에서만</h4><p>컴포넌트 CSS에는 색, 크기, 간격 값을 직접 적지 않아요. 다크 화면은 토큰만 바꿔서 만들어요.</p></div>
    </div>
  </section>

  <section id="tokens"><h2>토큰</h2><p>색, 글자 크기 9단계, 간격 8단계, 모서리 3개, 그림자 2개, 움직임 곡선 2개예요. 오른쪽 위 달 버튼으로 다크 값도 볼 수 있어요.</p>
    <h3>바탕과 글자</h3><div class="swatches">${sw("종이", "--paper", "모든 화면 바탕")}${sw("면", "--surface", "카드, 칸")}${sw("들어간 면", "--sunken")}${sw("선", "--line")}${sw("진한 선", "--line-strong")}${sw("글자", "--ink")}${sw("보조 글자", "--sub")}${sw("흐린 글자", "--muted")}${sw("가장 흐린", "--faint")}</div>
    <h3>강조와 뜻이 있는 색</h3><div class="swatches">${sw("강조", "--accent", "버튼, 링크, 지금 위치")}${sw("강조 옅게", "--accent-soft")}${sw("실행", "--run", "새 챕터, 맞음")}${sw("오류", "--error")}${sw("확인", "--check", "꿀팁, 주의")}</div>
    <h3>분류색 6개</h3><div class="swatches">${Object.entries(TK).map(([l, k]) => sw(l, `--t-${k}`, `옅게 --t-${k}-soft`)).join("")}</div>
    <h3>글자</h3><div class="grid g2"><div class="scale">
      <div><code>40 / 800</code><span style="font-size:40px;font-weight:800;letter-spacing:-.035em">홈 제목</span></div>
      <div><code>32 / 800</code><span style="font-size:32px;font-weight:800;letter-spacing:-.03em">장 제목</span></div>
      <div><code>24 / 800</code><span style="font-size:24px;font-weight:800">구역 제목</span></div>
      <div><code>20 / 800</code><span style="font-size:20px;font-weight:800">단계 제목</span></div>
      <div><code>16 / 700</code><span style="font-weight:700">카드 제목</span></div>
      <div><code>16 / 400</code><span>본문은 16px, 줄 간격 1.6이에요.</span></div>
      <div><code>14 / 400</code><span style="font-size:14px">카드 설명, 표</span></div>
      <div><code>13 / 12</code><span style="font-size:13px;color:var(--muted)">레벨, 날짜, 단축키</span></div>
    </div><div class="scale">
      <div><code>Pretendard</code><span>가나다 ABC 0123 본문 글꼴</span></div>
      <div><code>JetBrains Mono</code><span class="mono" style="font-size:16px">SELECT * FROM 회원;</span></div>
      <div><code>+ D2Coding 한글</code><span class="mono" style="font-size:16px;white-space:normal">kant_shop=# 한글 칸 맞춤</span></div>
    </div></div>
    <h3>간격, 모서리, 그림자</h3><div class="grid g3">
      <div class="space">${[4, 8, 12, 16, 24, 32, 48, 64].map((n, j) => `<div><code style="width:44px">--s-${j + 1}</code><i style="width:${n}px"></i>${n}</div>`).join("")}</div>
      <div class="row" style="align-items:flex-start">${["sm", "md", "lg"].map((r) => `<div><div style="width:64px;height:64px;background:var(--surface);border:1px solid var(--line-strong);border-radius:var(--r-${r})"></div><span class="label">--r-${r}</span></div>`).join("")}</div>
      <div class="row" style="align-items:flex-start;gap:24px">${["raised", "float"].map((r) => `<div><div style="width:96px;height:64px;background:var(--surface);border-radius:var(--r-md);box-shadow:var(--shadow-${r})"></div><span class="label">--shadow-${r}</span></div>`).join("")}</div>
    </div>
  </section>

  <section id="brand"><h2>로고와 아이콘</h2><p>사이트 로고는 계단 하나예요. 다섯 단계를 한 칸씩 오른다는 뜻이고, 홈 히어로의 계단 그림과 같은 모양이에요.</p>
    <div class="grid g3" style="margin-top:24px">
      <div class="box"><h4>BrandMark</h4><div class="row" style="margin-top:12px">${brandEl("#")}</div><div class="row" style="margin-top:16px">${[48, 30, 20].map((s) => `<span class="brand-mark" style="width:${s}px;height:${s}px;border-radius:${s * .27}px"><svg viewBox="0 0 24 24" style="width:${s * .66}px;height:${s * .66}px" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19h5v-5h5V9h6"/></svg></span>`).join("")}<span class="label" style="margin:0">48 · 30 · 파비콘 20</span></div></div>
      <div class="box" style="grid-column:span 2"><h4>LogoTile: 도구 로고</h4><p>Simple Icons(CC0) 모양을 원래 색 그대로, 같은 크기 흰 타일 안에 둬요. 없는 두 개(터미널, 데이터베이스)는 Lucide 선 아이콘이에요.</p><div class="row" style="margin-top:12px">${Object.keys(LOGO).map((k) => `<div style="text-align:center">${tile(k, 44)}<span class="label" style="font-family:var(--font-sans)">${LOGO[k].title}</span></div>`).join("")}</div></div>
    </div>
    <div class="box" style="margin-top:16px"><h4>화면 아이콘</h4><p>Lucide(ISC) 선 아이콘 하나만 써요. 18px, 선 두께 1.75, 색은 글자색을 따라가요.</p><div class="row" style="margin-top:12px;gap:18px;color:var(--sub)">${["search", "sun", "moon", "menu", "panel-left", "arrow-right", "chevron-right", "download", "external-link", "lightbulb", "copy", "info", "triangle-alert", "circle-x", "x", "keyboard"].map((n) => `<span title="${n}">${i(n)}</span>`).join("")}</div></div>
  </section>

  <section id="thumb"><h2>썸네일</h2><p>그림 파일 없이 CSS로 그려요. 챕터가 늘어도 curriculum.json에 keyword 한 줄만 적으면 돼요.</p>
    <div class="grid g2" style="margin-top:24px;align-items:center">
      <div class="anat">${thumb(sample).replace('class="thumb', 'style="border-radius:14px;border:1px solid var(--line)" class="thumb')}</div>
      <ol class="legend"><li><b>1</b>바탕: 분류색의 옅은 색에 20px 모눈. 덱의 종이 느낌을 이어요.</li><li><b>2</b>번호: 고정폭 글꼴, 분류색. 배우는 순서를 먼저 보여 줘요.</li><li><b>3</b>도구 로고: 흰 타일, 두 도구를 쓰는 장은 둘까지.</li><li><b>4</b>코드 한 줄: 그 장에서 처음 치는 명령. 챕터마다 다른 부분은 여기 하나예요.</li></ol>
    </div>
    <h3>분류마다 한 장씩</h3><div class="cards">${["01", "03", "11", "23", "31", "40"].map((n) => card(byNo[n])).join("")}</div>
  </section>

  <section id="comp"><h2>컴포넌트</h2><p>이름은 코드의 컴포넌트 이름과 같아요. 지금 사이트의 컴포넌트 15개를 아래 19개로 정리해요.</p>
    <h3>Button</h3><div class="row"><a class="btn primary" href="#">01부터 시작하기 ${i("arrow-right")}</a><a class="btn secondary" href="#">강의 둘러보기</a><a class="btn ghost" href="#">취소</a><a class="btn secondary sm" href="#">${i("download")}PDF 받기</a></div>
    <span class="label">primary는 한 화면에 하나 · secondary · ghost · sm</span>
    <h3>FilterTabs · Level · NewTag</h3><div class="row"><div class="tabs"><button class="tab" aria-pressed="true">전체 <small>46</small></button><button class="tab t-git" aria-pressed="false"><span class="sw"></span>Git <small>7</small></button><button class="tab t-py" aria-pressed="false"><span class="sw"></span>파이썬 <small>21</small></button></div>${lvl("입문")}${lvl("기초")}${lvl("응용")}<span class="tag-new" style="margin:0">새 챕터</span></div>
    <h3>SearchButton · SearchDialog</h3><div class="row"><button class="search-btn" type="button" data-search>${i("search")}<span class="lbl">강의 찾기</span><kbd>/</kbd></button><span class="label" style="margin:0">누르거나 / , Ctrl K로 열어요. 제목과 keyword로 찾아요.</span></div>
    <h3>ChapterCard · TipCard · NewsItem</h3>
    <div class="grid g3" style="align-items:start">${card(byNo["22"])}<a class="tip" href="#"><span class="tip-ic">${i("lightbulb")}</span><div><h3>터미널 환경에 적응하기</h3><p>탐색기와 터미널 맞춰 보기, -h와 --help</p></div></a><a class="news-i" href="#"><span class="k"><b>업데이트</b>2026.11.23</span><h3>PDF로 받을 수 있어요</h3><p>슬라이드 아래 막대와 표에서 PDF를 바로 받아요.</p></a></div>
    <h3>NoticeBar · StageHeader · SectionHeader</h3>
    <div class="notice"><span class="k">공지</span><p>12월 수업부터 머신러닝 챕터가 이어서 올라와요.</p><button class="icon-btn" type="button" aria-label="닫기">${i("x")}</button></div>
    <div class="stage" style="padding-top:24px"><header class="stage-h" style="margin:0"><span class="n">4단계</span><h3>SQL</h3><small>36–44</small><p>${esc(stages[3].summary)}</p></header></div>
    <h3>Breadcrumb · Callout · CodeBlock</h3>
    <nav class="crumb"><a href="#">강의</a>${i("chevron-right")}<a href="#">4단계 SQL</a>${i("chevron-right")}<span>표 만들고 고르기</span></nav>
    <div class="grid g3" style="margin-top:16px"><div class="callout">${i("info")}<div>실습 칸에서 바로 쳐 봐요.</div></div><div class="callout warn">${i("triangle-alert")}<div>WHERE를 빼면 모든 줄이 바뀌어요.</div></div><div class="callout err">${i("circle-x")}<div><code>column does not exist</code></div></div></div>
    <div class="grid g2" style="margin-top:16px"><div class="code"><button class="copy" type="button" aria-label="복사">${i("copy")}</button>scores = [90, 85, 77]
print(sum(scores))</div><div class="code term"><button class="copy" type="button" aria-label="복사">${i("copy")}</button><span class="d">$</span> git log --oneline
<span class="d">a1b2c3d (HEAD -&gt; main) feat: 첫 커밋</span></div></div>
    <h3>나머지</h3>
    <p style="color:var(--sub);font-size:14px">Header, SiteFooter, Sidebar(장 목록, 파트로 묶음, 접기), PlayerFrame(덱 플레이어 iframe), Prose(챕터 README), PrevNext, RoadmapSteps(홈 계단)는 화면 시안에서 봐요.</p>
    <h3>지금 컴포넌트와 짝</h3><div class="tablewrap"><table class="cmp"><thead><tr><th>지금</th><th>v2</th><th>바뀌는 점</th></tr></thead><tbody>
      <tr><td>Thumb</td><td>Thumb</td><td>브랜드 색 바탕과 무늬 4가지를 빼고, 분류색 모눈 + 코드 한 줄</td></tr>
      <tr><td>CurriculumList</td><td>FilterTabs + StageHeader + ChapterCard</td><td>카드 표시 다섯 개를 셋으로. NEW는 날짜 기준</td></tr>
      <tr><td>LogoTile</td><td>LogoTile</td><td>타일 색을 로고 색으로 칠하지 않고 늘 흰 타일</td></tr>
      <tr><td>Header, AppShell</td><td>Header + Sidebar</td><td>홈은 위 메뉴와 찾기만, 사이드바는 장 화면에만</td></tr>
      <tr><td>홈 hero, cloud, stats</td><td>RoadmapSteps</td><td>어두운 히어로, 반짝이 배지, 숫자 통계, 로고 구름을 빼고 계단 하나</td></tr>
      <tr><td>NewsList, news-bar</td><td>NoticeBar + NewsItem</td><td>공지 한 줄과 소식 카드 셋으로 나눔</td></tr>
      <tr><td>DeckLayout</td><td>Sidebar + PlayerFrame + Prose</td><td>장 목록을 파트로 묶고 한 줄로. 오른쪽에 이 챕터 목차</td></tr>
    </tbody></table></div>
  </section>

  <section id="screens"><h2>화면</h2><p>넓은 화면(1440px)과 휴대폰(390px)에서 찍었어요. 눌러서 실제 화면을 열어요.</p>
    <h3>홈</h3><div class="screens"><a class="shot" href="home.html"><img src="img/home-1440.png" alt="홈 넓은 화면"><span>넓은 화면 ${i("arrow-right")}</span></a><a class="shot" href="home.html"><img src="img/home-390.png" alt="홈 휴대폰"><span>휴대폰 ${i("arrow-right")}</span></a></div>
    <h3>장 화면</h3><div class="screens"><a class="shot" href="chapter.html"><img src="img/chapter-1440.png" alt="장 화면 넓은 화면"><span>넓은 화면 ${i("arrow-right")}</span></a><a class="shot" href="chapter.html"><img src="img/chapter-390.png" alt="장 화면 휴대폰"><span>휴대폰 ${i("arrow-right")}</span></a></div>
    <h3>찾기와 다크</h3><div class="screens" style="grid-template-columns:1fr 1fr"><a class="shot" href="home.html"><img src="img/search-1440.png" alt="찾기 창"><span>찾기 (/ , Ctrl K)</span></a><a class="shot" href="home.html"><img src="img/home-dark-1440.png" alt="다크 화면"><span>다크 화면</span></a></div>
  </section>
</main>
${footer}`, docCss);
fs.writeFileSync(path.join(HERE, "index.html"), doc);
console.log("v2 시안: index.html, home.html, chapter.html");
