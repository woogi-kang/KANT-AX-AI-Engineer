// 시안 v4 "그림책": 밝은 바탕, 묶음마다 다른 그림(SVG)으로 개념을 보여 줘요. site 폴더에서 node design/v4/gen.mjs
import { i, tile, esc, inline, chapters, stages, extras, news, NOTICE, C, goals, before, parts, slides, prev, next, page, FOOT, write, LV } from "../lib.mjs";

/* 묶음 19개의 그림. 색은 --c(분류색), --m(중간), --s(옅은 색), 흰색만 써요. viewBox 320x200 */
const W = "#fff";
const box = (x, y, w, h, r = 10, f = W, extra = "") => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${f}" ${extra}/>`;
const ln = (d, w = 6, c = "var(--c)") => `<path d="${d}" fill="none" stroke="${c}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`;
const dot = (x, y, r = 12, f = "var(--c)", extra = "") => `<circle cx="${x}" cy="${y}" r="${r}" fill="${f}" ${extra}/>`;
const tx = (x, y, t, s = 22, f = "var(--c)", w = 700) => `<text x="${x}" y="${y}" font-family="JetBrains Mono, D2Coding Hangul, monospace" font-size="${s}" font-weight="${w}" fill="${f}" text-anchor="middle">${t}</text>`;
const table = (x, y, cols, rows, cw, rh, hi = -1) => {
  let o = box(x, y, cols * cw, (rows + 1) * rh, 8);
  o += `<rect x="${x}" y="${y}" width="${cols * cw}" height="${rh}" rx="8" fill="var(--c)"/><rect x="${x}" y="${y + rh - 8}" width="${cols * cw}" height="8" fill="var(--c)"/>`;
  for (let r = 0; r < rows; r++) {
    if (r === hi) o += `<rect x="${x}" y="${y + (r + 1) * rh}" width="${cols * cw}" height="${rh}" fill="var(--m)"/>`;
    for (let c = 0; c < cols; c++) o += `<rect x="${x + c * cw + 10}" y="${y + (r + 1) * rh + rh / 2 - 3}" width="${cw - 24}" height="6" rx="3" fill="var(--s2)"/>`;
  }
  return o;
};
const cyl = (x, y, w, h) => `<path d="M${x} ${y + 14}v${h - 28}c0 8 ${w / 4} 14 ${w / 2} 14s${w / 2}-6 ${w / 2}-14v-${h - 28}" fill="${W}"/><ellipse cx="${x + w / 2}" cy="${y + 14}" rx="${w / 2}" ry="14" fill="var(--c)"/>${ln(`M${x} ${y + h / 2}c0 8 ${w / 4} 14 ${w / 2} 14s${w / 2}-6 ${w / 2}-14`, 4, "var(--m)")}`;
const ART = [
  /* 0 터미널 */ box(70, 40, 180, 120, 14) + `<rect x="70" y="40" width="180" height="28" rx="14" fill="var(--c)"/><rect x="70" y="54" width="180" height="14" fill="var(--c)"/>` + dot(90, 54, 5, W) + dot(106, 54, 5, W) + tx(112, 112, "&gt;_", 34) + `<rect x="150" y="90" width="14" height="30" rx="2" fill="var(--m)"/>`,
  /* 1 Git 혼자 */ ln("M40 100H280", 6) + dot(70, 100, 16) + dot(140, 100, 16) + dot(210, 100, 16) + dot(270, 100, 18, W, 'stroke="var(--c)" stroke-width="6"') + box(236, 44, 70, 26, 13, "var(--c)") + tx(271, 63, "main", 15, W),
  /* 2 Git 같이 */ ln("M40 130H280", 6) + ln("M100 130C130 130 130 70 160 70H200C230 70 230 130 250 130", 6, "var(--m)") + dot(56, 130, 14) + dot(100, 130, 14) + dot(170, 70, 14, "var(--m)") + dot(210, 70, 14, "var(--m)") + dot(250, 130, 17, W, 'stroke="var(--c)" stroke-width="6"'),
  /* 3 파이썬 작업 환경 */ `<path d="M70 70h60l14 16h106v84H70z" fill="var(--m)"/>` + box(70, 86, 180, 84, 10) + box(110, 110, 100, 40, 8, "var(--c)") + tx(160, 137, ".venv", 18, W),
  /* 4 터미널에서 GitHub */ box(40, 70, 110, 80, 12) + tx(95, 120, "$ gh", 20) + ln("M165 110H200", 6, "var(--m)") + ln("M190 98L204 110L190 122", 6, "var(--m)") + `<path d="M230 128a28 28 0 0 1 4-56 34 34 0 0 1 60 10 24 24 0 0 1-4 46z" fill="${W}"/>` + dot(262, 106, 10),
  /* 5 기초 문법과 자료형 */ [0, 1, 2, 3].map((k) => box(52 + k * 56, 74, 48, 48, 8) + tx(76 + k * 56, 106, ["3", "a", "7", "x"][k], 20) + tx(76 + k * 56, 146, String(k), 14, "var(--m)", 500)).join(""),
  /* 6 제어문 */ `<path d="M160 34l44 36-44 36-44-36z" fill="var(--c)"/>` + tx(160, 77, "if", 20, W) + ln("M116 70H70V130", 5, "var(--m)") + ln("M204 70H250V130", 5, "var(--m)") + box(36, 130, 68, 40, 8) + box(216, 130, 68, 40, 8) + tx(70, 157, "T", 18) + tx(250, 157, "F", 18),
  /* 7 함수 */ ln("M40 100H110", 6, "var(--m)") + ln("M100 88L112 100L100 112", 6, "var(--m)") + box(118, 56, 84, 88, 14, "var(--c)") + tx(160, 112, "f()", 26, W) + ln("M210 100H276", 6, "var(--m)") + ln("M266 88L278 100L266 112", 6, "var(--m)"),
  /* 8 클래스 */ `<rect x="40" y="60" width="96" height="80" rx="40" fill="none" stroke="var(--c)" stroke-width="6" stroke-dasharray="10 8"/>` + tx(88, 108, "틀", 22) + ln("M150 100H176", 5, "var(--m)") + `<rect x="190" y="48" width="86" height="48" rx="24" fill="var(--c)"/><rect x="190" y="108" width="86" height="48" rx="24" fill="var(--m)"/>`,
  /* 9 미니 프로젝트 */ [0, 1, 2].map((k) => box(70 + k * 34, 40 + k * 14, 110, 120, 10, k === 2 ? W : "var(--m)") ).join("") + [0, 1, 2, 3].map((k) => `<rect x="152" y="${92 + k * 18}" width="${70 - k * 10}" height="6" rx="3" fill="var(--c)"/>`).join(""),
  /* 10 Docker 기초 */ [[60, 110], [130, 110], [200, 110], [95, 60], [165, 60]].map(([x, y]) => box(x, y, 64, 44, 6, x === 95 ? "var(--c)" : W) + [1, 2, 3].map((k) => `<rect x="${x + k * 16 - 2}" y="${y + 8}" width="4" height="28" rx="2" fill="${x === 95 ? W : "var(--m)"}"/>`).join("")).join("") + ln("M40 166H280", 6),
  /* 11 웹 서버 */ box(36, 56, 110, 88, 10) + `<rect x="36" y="56" width="110" height="22" rx="10" fill="var(--m)"/>` + ln("M160 92H200", 5) + ln("M190 82L202 92L190 102", 5) + ln("M200 116H160", 5, "var(--m)") + ln("M170 106L158 116L170 126", 5, "var(--m)") + box(216, 50, 70, 100, 10, "var(--c)") + `<rect x="230" y="70" width="42" height="8" rx="4" fill="${W}"/><rect x="230" y="90" width="42" height="8" rx="4" fill="${W}"/>`,
  /* 12 데이터베이스 기초 */ cyl(110, 40, 100, 120),
  /* 13 데이터베이스 컨테이너 */ box(70, 46, 180, 116, 12, "var(--m)") + [1, 2, 3, 4, 5].map((k) => `<rect x="${70 + k * 30 - 3}" y="56" width="6" height="96" rx="3" fill="var(--s)"/>`).join("") + cyl(120, 60, 80, 90),
  /* 14 표 만들고 고르기 */ table(60, 46, 4, 4, 50, 22, 2),
  /* 15 조건, 집계, 합치기 */ table(30, 60, 2, 3, 46, 20) + table(198, 60, 2, 3, 46, 20) + ln("M134 100H186", 5, "var(--m)") + dot(160, 100, 14, "var(--c)") + tx(160, 107, "+", 20, W),
  /* 16 넣고 고치고 되돌리기 */ table(40, 54, 3, 3, 46, 22, 1) + ln("M230 80a40 40 0 1 1 -6 52", 7, "var(--c)") + ln("M222 62L232 82L212 88", 7, "var(--c)"),
  /* 17 파이썬에서 SQL */ box(40, 66, 100, 70, 10) + tx(90, 110, "py", 24) + ln("M152 92H182", 5, "var(--m)") + ln("M182 112H152", 5, "var(--m)") + cyl(196, 52, 84, 100),
  /* 18 표 다루기 */ [50, 80, 40, 100, 70].map((h, k) => `<rect x="${60 + k * 42}" y="${160 - h}" width="28" height="${h}" rx="6" fill="${k === 3 ? "var(--c)" : W}"/>`).join("") + ln("M44 164H276", 5, "var(--m)"),
];
const art = (gi, cls = "art") => `<svg class="${cls}" viewBox="0 0 320 200" aria-hidden="true">${ART[gi]}</svg>`;

const css = `
:root{--bg:#FFFDF8;--card:#FFFFFF;--soft:#F5F2EA;--line:#ECE7DC;--ink:#1F2430;--sub:#4E5566;--muted:#7B8190;--accent:#2459C9;--accent-soft:#E7EEFC;
 --term:#5B6474;--term-s:#ECEEF2;--term-m:#C9CED8;--git:#C7741E;--git-s:#FBEEDC;--git-m:#F0C58D;--gh:#6E52CF;--gh-s:#EFEAFB;--gh-m:#C9BBF2;
 --py:#2E6DC2;--py-s:#E6EFFB;--py-m:#A9C6EE;--docker:#14899A;--docker-s:#DDF2F3;--docker-m:#93D3D9;--db:#B9478A;--db-s:#F8E6F0;--db-m:#E9A9CD}
body{background:var(--bg);color:var(--ink);font-size:16px;line-height:1.6}
.t-term{--c:var(--term);--s:var(--term-s);--m:var(--term-m)}.t-git{--c:var(--git);--s:var(--git-s);--m:var(--git-m)}.t-gh{--c:var(--gh);--s:var(--gh-s);--m:var(--gh-m)}
.t-py{--c:var(--py);--s:var(--py-s);--m:var(--py-m)}.t-docker{--c:var(--docker);--s:var(--docker-s);--m:var(--docker-m)}.t-db{--c:var(--db);--s:var(--db-s);--m:var(--db-m)}
[class*="t-"]{--s2:color-mix(in srgb,var(--m) 60%,#fff)}
.wrap{max-width:1200px;margin:0 auto;padding:0 24px}
.logo-tile{--sz:30px;width:var(--sz);height:var(--sz);border-radius:9px;background:#fff;box-shadow:0 0 0 1px rgba(31,36,48,.08);display:grid;place-items:center;flex:none}.logo-tile svg{width:60%;height:60%}
.hd{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 90%,transparent);backdrop-filter:blur(10px)}
.hd .wrap{height:68px;display:flex;align-items:center;gap:28px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:17px;letter-spacing:-.02em;white-space:nowrap}
.mark{width:34px;height:34px;border-radius:11px;background:var(--accent);display:grid;place-items:center}.mark svg{width:22px;height:22px}
.nav{display:flex;gap:6px}.nav a{padding:8px 14px;border-radius:999px;font-weight:600;font-size:15px;color:var(--sub)}.nav a:hover{background:var(--soft)}.nav a[aria-current]{background:var(--ink);color:#fff}
.hd-r{margin-left:auto;display:flex;gap:8px;align-items:center}
.sbtn{display:flex;align-items:center;gap:8px;height:40px;padding:0 16px;border-radius:999px;border:0;background:var(--soft);color:var(--muted);font-size:14px;cursor:pointer;min-width:220px}
.sbtn span{flex:1;text-align:left}kbd{font-size:12px;color:var(--muted)}
.ib{width:40px;height:40px;border-radius:999px;border:0;background:none;color:var(--sub);display:grid;place-items:center;cursor:pointer}.ib:hover{background:var(--soft)}
.om{display:none}
@media (max-width:760px){.nav,.sbtn span,.sbtn kbd{display:none}.sbtn{min-width:0;width:40px;padding:0;justify-content:center;background:none}.om{display:grid}.hd-r{gap:0}}
.hero{text-align:center;padding:56px 0 24px}
.hero h1{font-size:44px;line-height:1.22;letter-spacing:-.04em;font-weight:800}
.hero h1 em{font-style:normal;color:var(--accent)}
.hero p{font-size:18px;color:var(--sub);margin:16px auto 0;max-width:32em}
.cta{display:flex;gap:10px;justify-content:center;margin-top:28px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:8px;height:48px;padding:0 24px;border-radius:999px;font-weight:700;font-size:16px;white-space:nowrap}
.btn.p{background:var(--accent);color:#fff}.btn.s{background:var(--card);box-shadow:0 0 0 1px var(--line)}.btn.sm{height:38px;padding:0 16px;font-size:14px}
.path{position:relative;display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin:48px 0 8px;list-style:none;padding:0}
.path::before{content:"";position:absolute;left:8%;right:8%;top:62px;border-top:3px dashed var(--line)}
.path li{position:relative;text-align:center}
.path a{display:block}
.path .ill{width:124px;height:124px;margin:0 auto;border-radius:50%;background:var(--s);display:grid;place-items:center;transition:transform .25s cubic-bezier(.25,.8,.25,1)}
.path a:hover .ill{transform:translateY(-4px)}
.path .ill svg{width:112px;height:70px}
.path b{display:block;margin-top:14px;font-size:16px;letter-spacing:-.02em}
.path small{display:block;color:var(--muted);font-size:13px;margin-top:2px}
.path .n{position:absolute;top:0;left:calc(50% + 34px);width:28px;height:28px;border-radius:50%;background:var(--ink);color:#fff;font-size:13px;font-weight:700;display:grid;place-items:center}
.notice{display:flex;gap:12px;align-items:center;margin-top:40px;padding:14px 20px;border-radius:16px;background:var(--accent-soft);font-size:15px;color:var(--sub)}
.notice .i{color:var(--accent)}
.sec{padding-top:72px}
.sec-h{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin-bottom:20px;flex-wrap:wrap}
.sec-h h2{font-size:30px;font-weight:800;letter-spacing:-.03em}.sec-h p{color:var(--muted);margin-top:2px}
.more{color:var(--accent);font-weight:700;font-size:15px;display:flex;gap:4px;align-items:center}
.chips{display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;padding:2px}
.chips button{height:38px;padding:0 16px;border-radius:999px;border:0;background:var(--card);box-shadow:0 0 0 1px var(--line);font-size:14px;font-weight:600;color:var(--sub);cursor:pointer;white-space:nowrap}
.chips button[aria-pressed="true"]{background:var(--ink);color:#fff;box-shadow:none}
.stage{padding-top:44px}
.stage-h{display:flex;align-items:center;gap:12px;margin-bottom:18px}
.stage-h .n{width:36px;height:36px;border-radius:12px;background:var(--ink);color:#fff;font-weight:800;display:grid;place-items:center}
.stage-h b{font-size:22px;letter-spacing:-.03em}.stage-h small{color:var(--muted);font-size:14px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:20px}
.card{display:flex;flex-direction:column;background:var(--card);border-radius:20px;box-shadow:0 0 0 1px var(--line);overflow:hidden;transition:transform .25s cubic-bezier(.25,.8,.25,1),box-shadow .25s}
.card:hover{transform:translateY(-4px);box-shadow:0 0 0 1px var(--line),0 18px 36px rgba(31,36,48,.10)}
.pic{position:relative;background:var(--s);aspect-ratio:16/11;display:grid;place-items:center}
.pic .art{width:88%;height:auto;margin-bottom:30px}
.pic .kw{position:absolute;left:14px;bottom:12px;max-width:calc(100% - 28px);font:600 13px/1 "JetBrains Mono","D2Coding Hangul",monospace;color:var(--ink);background:#fff;border-radius:8px;padding:7px 10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pic .no{position:absolute;left:14px;top:12px;font:800 15px/1 "JetBrains Mono",monospace;color:var(--c);background:#fff;border-radius:999px;padding:6px 10px}
.pic .lg{position:absolute;right:12px;top:10px;display:flex;gap:6px}
.card-b{padding:16px 18px 18px;display:flex;flex-direction:column;gap:6px;flex:1}
.card-b small{font-size:13px;color:var(--c);font-weight:700}
.card-b h3{font-size:17px;line-height:1.4;letter-spacing:-.02em;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.lv{margin-top:auto;padding-top:6px;display:flex;align-items:center;gap:6px;font-size:13px;color:var(--muted)}
.lv i{display:flex;gap:3px}.lv i b{width:16px;height:6px;border-radius:3px;background:var(--line)}.lv i b.on{background:var(--c)}
.new{display:inline-block;margin-left:6px;padding:1px 8px;border-radius:999px;background:#E3F4EA;color:#1F8A4C;font-size:12px;font-weight:700;vertical-align:3px}
.tips{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px}
.tip{display:flex;gap:16px;align-items:flex-start;padding:22px;border-radius:20px;background:#FFF6E3}
.tip .ic{width:52px;height:52px;border-radius:16px;background:#fff;color:#B26A00;display:grid;place-items:center;flex:none}.tip .ic .i{width:26px;height:26px}
.tip h3{font-size:17px}.tip p{font-size:14px;color:var(--sub);margin-top:4px}
.rel{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}.rel span{background:#fff;border-radius:999px;padding:3px 10px;font-size:12px;color:var(--sub)}
.news{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.news a{padding:22px;border-radius:20px;background:var(--card);box-shadow:0 0 0 1px var(--line)}
.news .k{font-size:13px;color:var(--muted)}.news .k b{color:var(--accent);margin-right:8px}
.news h3{font-size:17px;margin-top:8px;line-height:1.4}.news p{font-size:14px;color:var(--sub);margin-top:6px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.ft{margin-top:80px;padding:28px 0 44px;border-top:1px solid var(--line);font-size:13px;color:var(--muted)}.ft .wrap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}.ft nav{display:flex;gap:16px}
@media (max-width:900px){.news{grid-template-columns:1fr}.path{grid-template-columns:repeat(5,minmax(120px,1fr));overflow-x:auto;padding-bottom:8px}.path::before{display:none}}
@media (max-width:640px){.wrap{padding:0 16px}.hero{padding:32px 0 8px;text-align:left}.hero h1{font-size:30px}.hero p{font-size:16px;margin-left:0}.cta{justify-content:flex-start}.cta .btn{flex:1;justify-content:center}
 .path{display:flex;flex-direction:column;gap:10px;margin-top:28px;overflow:visible}.path a{display:flex;align-items:center;gap:14px;text-align:left;padding:10px;border-radius:16px;background:var(--card);box-shadow:0 0 0 1px var(--line)}
 .path .ill{width:64px;height:64px;margin:0;border-radius:14px;flex:none}.path .ill svg{width:52px;height:34px}.path b{margin:0}.path small{margin:0}.path .n{position:static;order:-1;flex:none}
 .sec{padding-top:52px}.sec-h h2{font-size:24px}.cards{grid-template-columns:1fr 1fr;gap:12px}.card{border-radius:16px}.card-b{padding:12px}.card-b h3{font-size:14px}.card-b small{font-size:12px}.pic .no{font-size:12px;padding:4px 8px;left:8px;top:8px}.pic .kw{font-size:11px;left:8px;bottom:8px;padding:5px 7px;max-width:calc(100% - 16px)}.pic .art{margin-bottom:24px}.pic .lg{display:none}.tips{grid-template-columns:1fr}.notice{align-items:flex-start;font-size:14px}}
.dlg{position:fixed;inset:0;z-index:50;background:rgba(31,36,48,.35);display:none;justify-content:center;align-items:flex-start;padding:12vh 16px 0}.dlg[open]{display:flex}
.dlg-box{width:min(620px,100%);background:#fff;border-radius:24px;overflow:hidden;box-shadow:0 24px 60px rgba(31,36,48,.2)}
.dlg-in{display:flex;gap:10px;align-items:center;padding:0 20px;height:62px;border-bottom:1px solid var(--line)}.dlg-in input{flex:1;min-width:0;border:0;outline:0;font:inherit;font-size:18px}
.dlg-list{padding:8px;max-height:50vh;overflow:auto}.dlg-item{display:flex;gap:10px;padding:12px 14px;border-radius:14px;font-size:15px}.dlg-item b{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.dlg-item small{color:var(--muted);white-space:nowrap}
.dlg-item.on,.dlg-item:hover{background:var(--accent-soft)}.dlg-empty{padding:20px;text-align:center;color:var(--muted)}
/* 장 화면 */
.ch{max-width:1100px;margin:0 auto;padding:16px 24px 0}
.crumb{display:flex;gap:6px;align-items:center;font-size:14px;color:var(--muted);flex-wrap:wrap}.crumb .i{width:14px;height:14px}
.banner{display:grid;grid-template-columns:240px minmax(0,1fr);gap:28px;align-items:center;margin:18px 0 24px;padding:20px;border-radius:24px;background:var(--s)}
.banner .art{width:100%;height:auto;background:rgba(255,255,255,.5);border-radius:18px;padding:12px}
.banner small{font-weight:700;color:var(--c);font-size:14px}.banner h1{font-size:32px;letter-spacing:-.035em;line-height:1.25;margin-top:4px}
.banner p{color:var(--sub);margin-top:6px}.banner .act{display:flex;gap:8px;margin-top:16px;flex-wrap:wrap}
.player{aspect-ratio:16/9;border-radius:20px;overflow:hidden;background:#1D2330;box-shadow:0 0 0 1px var(--line)}.player iframe{width:100%;height:100%;border:0}
.goals{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;list-style:none;padding:0;margin:0}
.goals li{display:flex;gap:10px;padding:14px 16px;border-radius:16px;background:var(--card);box-shadow:0 0 0 1px var(--line);font-size:15px;line-height:1.6}
.goals li .i{color:var(--c);margin-top:3px}
.goals code,.prereq code{font-size:.84em;background:var(--soft);border-radius:6px;padding:1px 6px;white-space:nowrap}.prereq code{background:#fff;white-space:normal}
.h2{font-size:22px;letter-spacing:-.03em;margin:44px 0 14px}
.prereq{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}
.prereq a{display:flex;gap:12px;align-items:flex-start;padding:14px;border-radius:16px;background:var(--soft);font-size:14px;line-height:1.55}
.prereq a b{flex:none;width:34px;height:34px;border-radius:10px;background:#fff;display:grid;place-items:center;font:700 13px "JetBrains Mono",monospace}
.pn{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:44px}.pn a{display:flex;gap:14px;align-items:center;padding:14px;border-radius:20px;background:var(--card);box-shadow:0 0 0 1px var(--line)}
.pn .mini{width:88px;flex:none;border-radius:12px;background:var(--s)}.pn .mini svg{width:100%;height:auto}
.pn small{display:block;color:var(--muted);font-size:13px}.pn b{font-size:15px}.pn a:last-child{flex-direction:row-reverse;text-align:right}
@media (max-width:760px){.banner{grid-template-columns:1fr;gap:12px}.banner .art{max-width:200px}.goals{grid-template-columns:1fr}.pn{grid-template-columns:1fr}.pn a:last-child{flex-direction:row;text-align:left}}
@media (max-width:640px){.ch{padding:12px 16px 0}.banner{padding:16px;border-radius:20px}.banner h1{font-size:24px}.banner .act .btn{flex:1;justify-content:center}.player{border-radius:14px}}
`;
const markSvg = `<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19h5v-5h5V9h6"/><circle cx="20" cy="5" r="1.6" fill="#fff" stroke="none"/></svg>`;
const header = `<header class="hd"><div class="wrap"><a class="brand" href="home.html"><span class="mark">${markSvg}</span>풀스택 AI/AX 엔지니어</a>
<nav class="nav"><a href="home.html#lec" aria-current="page">강의</a><a href="home.html#tips">꿀팁</a><a href="home.html#news">소식</a></nav>
<div class="hd-r"><button class="sbtn" type="button" data-search>${i("search")}<span>무엇을 배워 볼까요?</span><kbd>/</kbd></button><button class="ib" type="button" aria-label="어둡게 보기">${i("moon")}</button><button class="ib om" type="button" aria-label="메뉴">${i("menu")}</button></div></div></header>`;
const foot = `<footer class="ft"><div class="wrap"><span>${FOOT}</span><nav><a href="#">이용 안내</a><a href="mailto:woogi@memoriz.net">문의</a></nav></div></footer>`;
const lv = (c) => `<span class="lv"><i>${[1, 2, 3].map((k) => `<b${k <= LV[c.level] ? ' class="on"' : ""}></b>`).join("")}</i>${c.level}</span>`;
const card = (c) => `<a class="card t-${c.tk}" href="chapter.html" data-t="${c.tk}"><div class="pic"><span class="no">${c.no}</span><span class="lg">${c.logos.map((k) => tile(k, 28)).join("")}</span>${art(c.gi)}<span class="kw">${esc(c.keyword)}</span></div><div class="card-b"><small>${esc(c.group)}</small><h3>${esc(c.title)}${c.no === "46" ? '<span class="new">새 챕터</span>' : ""}</h3>${lv(c)}</div></a>`;
const tracks = [["전체", "all"], ...["터미널", "Git", "GitHub", "파이썬", "Docker", "데이터베이스"].map((t) => [t, chapters.find((c) => c.track === t).tk])];
const home = page("v4 그림책 · 홈", "light", css, `${header}<main class="wrap">
<section class="hero"><h1>개발이 처음이어도<br><em>그림으로 먼저</em> 이해해요</h1><p>터미널부터 데이터 분석까지 ${chapters.length}개 챕터를, 애니메이션 슬라이드와 실제로 실행한 화면으로 배워요.</p>
<div class="cta"><a class="btn p" href="chapter.html">01부터 시작하기 ${i("arrow-right")}</a><a class="btn s" href="#lec">강의 둘러보기</a></div>
<ol class="path">${stages.map((s) => `<li class="t-${s.list[Math.floor(s.list.length / 2)].tk}"><a href="#stage-${s.no}"><span class="n">${s.no}</span><span class="ill">${art(s.groups[s.no === 1 ? 1 : 0].gi, "")}</span><span><b>${s.title}</b><small>${s.from}–${s.to} · ${s.list.length}챕터</small></span></a></li>`).join("")}</ol></section>
<div class="notice">${i("megaphone")}<span>${NOTICE}</span></div>
<section class="sec" id="lec"><div class="sec-h"><div><h2>강의</h2><p>순서대로 한 단계씩 올라가요</p></div><div class="chips">${tracks.map(([l, k]) => `<button type="button" data-f="${k}" aria-pressed="${k === "all"}">${l}</button>`).join("")}</div></div>
${stages.map((s) => `<section class="stage" id="stage-${s.no}" data-stage><div class="stage-h"><span class="n">${s.no}</span><b>${s.title}</b><small>${s.from}–${s.to}</small></div><div class="cards">${s.list.map(card).join("")}</div></section>`).join("")}</section>
<section class="sec" id="tips"><div class="sec-h"><div><h2>꿀팁</h2><p>막혔을 때 꺼내 봐요</p></div></div><div class="tips">${extras.map((e) => `<a class="tip" href="#"><span class="ic">${i("lightbulb")}</span><div><h3>${esc(e.title)}</h3><p>${inline(e.summary.split(", ").slice(0, 3).join(", "))}</p><div class="rel">${e.rel.map((c) => `<span>${c.no} ${esc(c.title.replace(/ \(.+\)$/, ""))}</span>`).join("")}</div></div></a>`).join("")}</div></section>
<section class="sec" id="news"><div class="sec-h"><div><h2>소식</h2><p>새 챕터와 바뀐 점</p></div><a class="more" href="#">전체 보기 ${i("chevron-right")}</a></div><div class="news">${news.map((n) => `<a href="#"><span class="k"><b>${n.k}</b>${n.d}</span><h3>${esc(n.t)}</h3><p>${esc(n.p)}</p></a>`).join("")}</div></section>
</main>${foot}`);
const chapter = page("v4 그림책 · 장 화면", "light", css, `${header}<main class="ch t-${C.tk}">
<nav class="crumb"><a href="home.html#lec">강의</a>${i("chevron-right")}<a href="#">${C.stage}단계 ${C.stageTitle}</a>${i("chevron-right")}<span>${C.group}</span></nav>
<header class="banner">${art(C.gi)}<div><small>${C.no} · ${C.group}</small><h1>${esc(C.title)}</h1><p>${inline(C.goal)}</p><div class="act"><a class="btn p sm" href="#">${i("play")}처음부터 보기</a><a class="btn s sm" href="#">${i("download")}PDF 받기</a><a class="btn s sm" href="#">${i("external-link")}새 창</a></div></div></header>
<div class="player"><iframe src="../../decks/${C.dir}/${C.slides}" title="슬라이드" loading="lazy"></iframe></div>
<h2 class="h2">이 챕터를 마치면</h2><ul class="goals">${goals.map((g) => `<li>${i("circle-check")}<span>${inline(g)}</span></li>`).join("")}</ul>
<h2 class="h2">먼저 보고 오면 좋아요</h2><div class="prereq">${before.map(([a, b]) => `<a href="#"><b>${b.split(",")[0]}</b><span>${inline(a)}</span></a>`).join("")}</div>
<nav class="pn"><a class="t-${prev.tk}" href="#"><span class="mini">${art(prev.gi, "")}</span><span><small>이전 챕터</small><b>${prev.no} · ${esc(prev.title)}</b></span></a><a class="t-${next.tk}" href="#"><span class="mini">${art(next.gi, "")}</span><span><small>다음 챕터</small><b>${next.no} · ${esc(next.title)}</b></span></a></nav>
</main>${foot}`);
write("v4", "home.html", home);
write("v4", "chapter.html", chapter);
console.log("v4 done");
