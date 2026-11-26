// 디자인 시안 v3~v5가 같이 쓰는 데이터와 조각이에요. curriculum.json, 챕터 README, 덱 HTML을 읽어요.
import fs from "node:fs";
import path from "node:path";
import * as si from "simple-icons";

export const SITE = path.resolve(import.meta.dirname, "..");
export const ROOT = path.resolve(SITE, "..");
export const cur = JSON.parse(fs.readFileSync(path.join(ROOT, "curriculum.json"), "utf8"));

/* 아이콘: lucide-react의 모양 데이터 */
const cache = {};
async function lucide(name) {
  let f = path.join(SITE, "node_modules/lucide-react/dist/esm/icons", name + ".mjs");
  const src = fs.readFileSync(f, "utf8");
  const re = /from .\.\/(.+?)\.mjs/.exec(src);
  if (!src.includes("__iconData") && re) f = path.join(path.dirname(f), re[1] + ".mjs");
  const mod = await import(f);
  return mod.__iconData.node.map(([t, a]) => `<${t} ${Object.entries(a).filter(([k]) => k !== "key").map(([k, v]) => `${k}="${v}"`).join(" ")}/>`).join("");
}
const NAMES = ["search", "sun", "moon", "menu", "arrow-right", "chevron-right", "chevron-left", "chevron-down", "download", "external-link", "panel-left", "lightbulb", "x", "square-terminal", "database", "copy", "info", "folder", "folder-open", "file-code", "file-text", "corner-down-left", "play", "circle-check", "megaphone", "sparkle"];
for (const n of NAMES) cache[n] = await lucide(n);
export const IC = cache;
export const i = (n, cls = "i") => `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true">${cache[n]}</svg>`;

/* 로고 */
const brand = (x) => ({ title: x.title, hex: "#" + x.hex, path: x.path });
export const LOGO = {
  terminal: { title: "터미널", hex: "#3F4757", lucide: "square-terminal" },
  database: { title: "데이터베이스", hex: "#A23B72", lucide: "database" },
  git: brand(si.siGit), github: brand(si.siGithub), uv: brand(si.siUv), jupyter: brand(si.siJupyter),
  python: brand(si.siPython), docker: brand(si.siDocker), nginx: brand(si.siNginx), mysql: brand(si.siMysql),
  postgresql: brand(si.siPostgresql), numpy: brand(si.siNumpy), pandas: brand(si.siPandas),
};
export const tile = (k, sz = 32, cls = "logo-tile") => {
  const L = LOGO[k];
  const g = L.lucide ? `<svg viewBox="0 0 24 24" fill="none" stroke="${L.hex}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${cache[L.lucide]}</svg>` : `<svg viewBox="0 0 24 24" fill="${L.hex}"><path d="${L.path}"/></svg>`;
  return `<span class="${cls}" style="--sz:${sz}px" title="${L.title}">${g}</span>`;
};
const BY_CH = { "01": "terminal", "09": "uv", "10": "jupyter", "11": "github", "31": "nginx", "32": "database", "33": "mysql", "34": "postgresql", "44": "python", "45": "numpy", "46": "pandas" };
const BY_TRACK = { 터미널: "terminal", Git: "git", GitHub: "github", 파이썬: "python", Docker: "docker", 데이터베이스: "postgresql" };
const SECOND = { "06": "github", "31": "docker", "33": "docker", "34": "docker", "44": "postgresql", "45": "pandas" };
export const TK = { 터미널: "term", Git: "git", GitHub: "gh", 파이썬: "py", Docker: "docker", 데이터베이스: "db" };
export const LV = { 입문: 1, 기초: 2, 응용: 3 };

export const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
export const inline = (s) => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>");
export const plain = (s) => s.replace(/`/g, "");

export const chapters = cur.chapters.map((c) => {
  const no = c.dir.slice(0, 2);
  const a = BY_CH[no] ?? BY_TRACK[c.track];
  const b = SECOND[no];
  return { ...c, no, tk: TK[c.track], logos: b ? [a, b] : [a] };
});
export const byNo = Object.fromEntries(chapters.map((c) => [c.no, c]));
let gi = 0;
export const stages = cur.stages.map((s, n) => {
  const groups = s.groups.map((g) => ({ ...g, gi: gi++, chapters: chapters.filter((c) => c.no >= g.from && c.no <= g.to) }));
  groups.forEach((g) => g.chapters.forEach((c) => Object.assign(c, { group: g.title, gi: g.gi, stage: n + 1, stageTitle: s.title })));
  const list = groups.flatMap((g) => g.chapters);
  return { ...s, no: n + 1, groups, list, logos: [...new Set(list.map((c) => c.logos[0]))], from: list[0].no, to: list.at(-1).no };
});
export const extras = cur.extras.map((e) => ({ ...e, rel: e.related.map((d) => byNo[d.slice(0, 2)]) }));
export const news = [
  { k: "새 챕터", d: "2026.11.24", t: "46 · " + byNo["46"].title, p: plain(byNo["46"].goal) },
  ...cur.updates.slice(-2).reverse().map((u) => ({ k: "업데이트", d: u.date.replace(/-/g, "."), t: u.title, p: plain(u.summary) })),
];
export const NOTICE = "12월 수업부터 머신러닝 챕터가 이어서 올라와요. 슬라이드 아래 PDF 받기로 미리 내려받을 수 있어요.";

/* 장 화면 예시: 36 */
export const C = byNo["36"];
const readme = fs.readFileSync(path.join(ROOT, C.dir, "README.md"), "utf8");
const sect = (name) => (readme.split(/^## /m).find((x) => x.startsWith(name)) ?? "").split("\n").slice(1).join("\n").trim();
export const goals = sect("학습 목표").split("\n").filter((l) => l.startsWith("- ")).map((l) => l.slice(2));
const rows = (md) => md.split("\n").filter((l) => l.startsWith("|")).slice(2).map((l) => l.split("|").slice(1, -1).map((x) => x.trim()));
export const before = rows(sect("시작하기 전에"));
export const parts = rows(sect("구성")).map(([p, range]) => { const [a, b] = range.split(/[–-]/).map(Number); return { p, a, b: b || a }; });
const deck = fs.readFileSync(path.join(ROOT, C.dir, C.slides), "utf8");
const strip = (h) => h.replace(/<br\s*\/?>/gi, " ").replace(/<[^>]+>/g, "").replace(/&nbsp;/g, " ").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();
export const slides = [...deck.matchAll(/<section\b([^>]*)>([\s\S]*?)<\/section>/g)].map((m, n) => {
  const h = /<h([1-3])\b[^>]*>([\s\S]*?)<\/h\1>/.exec(m[2].replace(/<aside\b[\s\S]*?<\/aside>/g, ""));
  return { n: n + 1, t: h ? strip(h[2]) : `${n + 1}쪽` };
});
export const prev = byNo["35"], next = byNo["37"];
export const cut = (s, n) => (s.length > n ? s.slice(0, n - 1) + "…" : s);

/* 글꼴 (v2 폴더의 파일을 같이 써요) */
export const FONTS = `@font-face{font-family:"Pretendard";font-weight:45 920;font-display:swap;src:url("../v2/fonts/PretendardVariable.woff2") format("woff2-variations")}
@font-face{font-family:"JetBrains Mono";font-weight:100 800;font-display:swap;src:url("../v2/fonts/jetbrains-mono-latin-wght-normal.woff2") format("woff2")}
@font-face{font-family:"D2Coding Hangul";font-weight:400;font-display:swap;size-adjust:120%;unicode-range:U+AC00-D7A3,U+3131-318E;src:url("../v2/fonts/d2coding-hangul-400.woff2") format("woff2")}
@font-face{font-family:"D2Coding Hangul";font-weight:700;font-display:swap;size-adjust:120%;unicode-range:U+AC00-D7A3,U+3131-318E;src:url("../v2/fonts/d2coding-hangul-700.woff2") format("woff2")}
*,*::before,*::after{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:"Pretendard","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;word-break:keep-all;overflow-wrap:break-word}
a{color:inherit;text-decoration:none}img,svg{display:block}h1,h2,h3,h4,p{margin:0}button{font:inherit;color:inherit}
.mono,code,kbd{font-family:"JetBrains Mono","D2Coding Hangul",ui-monospace,Menlo,monospace}
.i{width:18px;height:18px;flex:none;fill:none;stroke:currentColor;stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round}
:focus-visible{outline:2px solid #2459C9;outline-offset:2px}`;

/* 찾기 창: / 또는 Ctrl K. 시안마다 모양은 CSS로 바꿔요 */
const sdata = JSON.stringify([...chapters.map((c) => ({ t: `${c.no} · ${c.title}`, s: c.track, k: c.keyword })), ...cur.extras.map((e) => ({ t: e.title, s: "꿀팁", k: "" }))]);
export const searchDlg = `<div class="dlg" data-dlg role="dialog" aria-modal="true" aria-label="강의 찾기"><div class="dlg-box"><div class="dlg-in">${i("search")}<input type="text" placeholder="챕터 이름, 명령어로 찾아요" aria-label="찾을 말"><kbd>Esc</kbd></div><div class="dlg-list"></div></div></div>`;
export const script = `<script>(()=>{const d=document.documentElement;
document.querySelectorAll('[data-theme-toggle]').forEach(b=>b.onclick=()=>{d.dataset.theme=d.dataset.theme==='dark'?'light':'dark'});
const dlg=document.querySelector('[data-dlg]');const inp=dlg.querySelector('input'),list=dlg.querySelector('.dlg-list');const data=${sdata};
function draw(){const q=inp.value.trim().toLowerCase();const it=data.filter(x=>!q||(x.t+' '+x.k).toLowerCase().includes(q)).slice(0,8);list.innerHTML=it.map((x,j)=>'<a class="dlg-item'+(j?'':' on')+'" href="chapter.html"><b>'+x.t.replace(/</g,'&lt;')+'</b><small>'+x.s+'</small></a>').join('')||'<p class="dlg-empty">찾는 챕터가 없어요</p>'}
function open(){dlg.setAttribute('open','');inp.value='';draw();inp.focus()}
document.querySelectorAll('[data-search]').forEach(b=>b.onclick=open);inp.oninput=draw;dlg.onclick=e=>{if(e.target===dlg)dlg.removeAttribute('open')};
addEventListener('keydown',e=>{const t=e.target.tagName;if(e.key==='Escape')dlg.removeAttribute('open');else if(!dlg.hasAttribute('open')&&((e.key==='/'&&t!=='INPUT')||((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'))){e.preventDefault();open()}});
document.querySelectorAll('[data-scroll]').forEach(b=>b.onclick=()=>{const r=document.getElementById(b.dataset.scroll);r.scrollBy({left:(b.dataset.dir==='l'?-1:1)*r.clientWidth*.8,behavior:'smooth'})});
const tabs=document.querySelectorAll('[data-f]');tabs.forEach(b=>b.onclick=()=>{tabs.forEach(x=>x.setAttribute('aria-pressed',x===b));const f=b.dataset.f;document.querySelectorAll('[data-t]').forEach(c=>c.hidden=f!=='all'&&c.dataset.t!==f);document.querySelectorAll('[data-stage]').forEach(s=>s.hidden=!s.querySelector('[data-t]:not([hidden])'))});
})()</script>`;
export const page = (title, theme, css, body) => `<!doctype html><html lang="ko" data-theme="${theme}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title>
<link rel="preload" href="../v2/fonts/PretendardVariable.woff2" as="font" type="font/woff2" crossorigin><style>${FONTS}\n${css}</style></head><body>${body}${searchDlg}${script}</body></html>`;
export const FOOT = "© 2026 Taewook Kang (woogi) · 허락 없이 옮겨 싣거나 고쳐 배포할 수 없어요";
export const write = (dir, file, html) => { fs.mkdirSync(path.join(SITE, "design", dir), { recursive: true }); fs.writeFileSync(path.join(SITE, "design", dir, file), html); };
