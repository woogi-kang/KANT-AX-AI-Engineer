// 로드맵 레포(woogi-kang/ax-engineer-roadmap, MIT)를 읽어 시안에 쓸 내용만 snapshot.json으로 뽑아요.
// 실제 사이트에서는 빌드할 때 같은 일을 해요. 쓰는 법: ROADMAP_DIR=로드맵레포경로 node design/v9/snap.mjs
import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";

const R = process.env.ROADMAP_DIR;
if (!R) throw new Error("ROADMAP_DIR를 적어 주세요");
const rd = (f) => fs.readFileSync(path.join(R, f), "utf8");
const link = (s) => { const m = /\[([^\]]+)\]\(([^)]+)\)/.exec(s); return m ? { t: m[1], href: m[2] } : { t: s.trim() }; };
const strip = (s) => s.replace(/\*\*/g, "").replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").trim();
const table = (block) => block.split("\n").filter((l) => /^\|/.test(l) && !/^\|[\s|:-]+\|$/.test(l)).slice(1).map((l) => l.slice(1, -1).split(" | ").map((c) => c.trim().replace(/^\|\s*/, "")));
const between = (s, a, b) => { const i = s.indexOf(a); if (i < 0) return ""; const j = b ? s.indexOf(b, i + a.length) : -1; return s.slice(i + a.length, j < 0 ? undefined : j); };

const readme = rd("README.md");
const stageBlocks = readme.split(/\n### (\d)단계\. /).slice(1);
const stages = [];
for (let k = 0; k < stageBlocks.length; k += 2) {
  const body = stageBlocks[k + 1].split("\n## ")[0];
  const [title, ...rest] = body.split("\n");
  const text = rest.join("\n");
  const lede = strip(text.trim().split("\n\n")[0]);
  const checks = [...text.matchAll(/^- \[ \] (.+)$/gm)].map((m) => strip(m[1]));
  stages.push({ no: +stageBlocks[k], title: title.trim(), lede, checks, text });
}
const s1 = stages[0], s2 = stages[1], s3 = stages[2], s4 = stages[3], s5 = stages[4];
s1.docs = table(s1.text.split("<!--")[0]).map(([a, b]) => ({ ...link(a), d: strip(b) }));
s2.areas = table(s2.text).map(([a, b]) => ({ ...link(a), q: strip(b), id: link(a).href.split("/").pop().replace(".md", "") }));
s3.steps = [...s3.text.matchAll(/^\d+\. \[([^\]]+)\]\(([^)]+)\)/gm)].map((m) => ({ t: m[1], href: m[2] }));
s4.projects = table(s4.text).map(([a, b, c]) => ({ ...link(a), out: strip(b), need: strip(c) }));
s5.lede = strip(s5.text.trim().split("\n\n")[0]);
for (const s of stages) delete s.text;

const start = table(between(readme, "## 나에게 맞는 시작점", "직함보다")).map(([a, b, c]) => ({ who: a, go: strip(b), first: c }));
const hb = between(readme, "<!-- hiring-monthly:start -->", "<!-- hiring-monthly:end -->");
const hiring = { lede: strip(hb.trim().split("\n\n")[0]), rows: table(hb).map(([a, b, c]) => ({ type: a, n: +b, open: +c })), note: "재게시와 프로젝트 공고가 섞여 있어 고유 채용 수는 아닙니다." };
const toolkit = table(between(readme, "## 실무 템플릿", "현업·리더")).map(([a, b]) => ({ when: a, items: [...b.matchAll(/\[([^\]]+)\]/g)].map((m) => m[1]) }));
const role = table(between(readme, "## AX 엔지니어는 어떤 일을 하나요?", "[역할 모델")).map(([a, b]) => ({ does: a, not: b }));
const defn = strip(readme.split("\n# AX Engineer Roadmap")[1].split("\n\n")[2]);

const cs = rd("case-studies/README.md");
const cases = table(between(cs, "## 업무별 사례 목록", "사례명과")).map(([field, c, lv, ready, scope, p, ev]) => {
  const [area, industry] = field.split(" · ");
  const [diff, risk] = lv.split(" · ");
  return { area, industry, ...link(c), diff: +diff, risk, scope, p, ev: strip(ev) };
});
const pub = JSON.parse(rd("research/public-ax-cases.json")).cases;
const fail = JSON.parse(rd("research/ax-failure-cases.json")).cases;
const publicCases = { n: pub.length, kr: pub.filter((c) => c.region === "KR").length, sample: pub.filter((c) => ["K01", "K05", "K12", "G15", "G21", "G08"].includes(c.id)).map((c) => ({ id: c.id, org: c.organization, w: c.workflow.ko, ind: c.industry })) };
const failures = { n: fail.length, kr: fail.filter((c) => c.region === "KR").length };

const topicMd = rd("technical-foundations/software-and-api.md");
const version = (/최신 릴리스: `([^`]+)`/.exec(readme) || [])[1];
let commit = "";
try { commit = execSync("git log -1 --format=%h·%cs", { cwd: R }).toString().trim(); } catch {}

const out = { source: "woogi-kang/ax-engineer-roadmap", license: "MIT", version, commit, defn, role, start, stages, hiring, toolkit, cases, publicCases, failures, topicMd };
fs.writeFileSync(path.join(import.meta.dirname, "snapshot.json"), JSON.stringify(out, null, 1));
console.log("snapshot", stages.length, "stages", cases.length, "cases", version, commit);
