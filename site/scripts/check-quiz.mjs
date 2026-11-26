// 확인 문제(quiz.json) 점검: node scripts/check-quiz.mjs [챕터 폴더 일부]
// 모든 챕터의 quiz.json을 읽어 형식, 파트 이름(README 구성 표와 같은지), 쪽 번호(그 파트 안인지, 덱 장 수 안인지),
// 정답 번호, 겹친 보기와 id를 봐요. verify가 "py"인 문제는 code를 python3로 실행해서 출력이 정답 보기와 같은지 봐요.
// 하나라도 틀리면 실패로 끝나요.
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const ROOT = path.resolve(import.meta.dirname, "..", "..");
const cur = JSON.parse(fs.readFileSync(path.join(ROOT, "curriculum.json"), "utf8"));
const only = process.argv[2];
const errs = [];
let nQ = 0, nPy = 0, nCh = 0;

const sect = (md, name) => (md.split(/^## /m).find((x) => x.startsWith(name)) ?? "").split("\n").slice(1).join("\n").trim();
const parts = (md) =>
  sect(md, "구성").split("\n").filter((l) => l.startsWith("|")).slice(2)
    .map((l) => l.split("|").slice(1, -1).map((x) => x.trim()))
    .filter((r) => r.length >= 2 && /\d/.test(r[1]))
    .map(([name, range]) => {
      const [a, b] = range.split(/[–~-]/).map((x) => parseInt(x, 10));
      return { name: name.replace(/^\d+\s*[.·]\s*/, ""), from: a, to: b || a };
    });
const norm = (s) => s.replace(/`/g, "").trim();

for (const c of cur.chapters) {
  if (only && !c.dir.includes(only)) continue;
  const f = path.join(ROOT, c.dir, "quiz.json");
  if (!fs.existsSync(f)) continue;
  nCh++;
  const bad = (m) => errs.push(`${c.dir}: ${m}`);
  let quiz;
  try { quiz = JSON.parse(fs.readFileSync(f, "utf8")); } catch (e) { bad(`JSON을 못 읽어요 ${e.message}`); continue; }
  const md = fs.readFileSync(path.join(ROOT, c.dir, "README.md"), "utf8");
  const ps = parts(md);
  const deck = fs.readFileSync(path.join(ROOT, c.dir, c.slides), "utf8");
  const pages = (deck.match(/<section\b/g) ?? []).length;
  const ids = new Set();
  const answers = [];
  for (const p of quiz.parts ?? []) {
    const meta = ps.find((x) => x.name === p.part);
    if (!meta) { bad(`README 구성 표에 없는 파트 "${p.part}" (있는 파트: ${ps.map((x) => x.name).join(", ")})`); continue; }
    if (!Array.isArray(p.questions) || p.questions.length < 2 || p.questions.length > 3) bad(`"${p.part}" 문제는 2~3개예요 (지금 ${p.questions?.length ?? 0}개)`);
    for (const q of p.questions ?? []) {
      nQ++;
      const at = `${q.id ?? "?"}`;
      if (!q.id || ids.has(q.id)) bad(`${at} id가 없거나 겹쳐요`);
      ids.add(q.id);
      for (const k of ["q", "explain"]) if (typeof q[k] !== "string" || !q[k].trim()) bad(`${at} ${k}가 비었어요`);
      if (!Array.isArray(q.choices) || q.choices.length < 2 || q.choices.length > 4) bad(`${at} 보기는 2~4개예요`);
      else if (new Set(q.choices.map(norm)).size !== q.choices.length) bad(`${at} 겹친 보기가 있어요`);
      if (!Number.isInteger(q.answer) || q.answer < 0 || q.answer >= (q.choices?.length ?? 0)) bad(`${at} 정답 번호가 보기 밖이에요`);
      answers.push(q.answer);
      if (!Number.isInteger(q.page) || q.page < meta.from || q.page > meta.to) bad(`${at} ${q.page}쪽은 "${p.part}"(${meta.from}–${meta.to}쪽) 밖이에요`);
      if (q.page > pages) bad(`${at} 덱은 ${pages}장인데 ${q.page}쪽이에요`);
      const text = [q.q, q.explain, q.code ?? "", ...(q.choices ?? [])].join(" ");
      if (/KANT/.test(text)) bad(`${at} 사이트에는 KANT라는 말을 쓰지 않아요`);
      if (q.verify === "py") {
        nPy++;
        if (!q.code) { bad(`${at} verify py인데 code가 없어요`); continue; }
        let out;
        try { out = execFileSync("python3", ["-I", "-c", q.code], { encoding: "utf8", env: { ...process.env, PYTHONHASHSEED: "0" }, timeout: 10000 }); }
        catch (e) { bad(`${at} 코드 실행 실패 ${String(e.stderr || e.message).trim().split("\n").pop()}`); continue; }
        const want = norm(q.choices[q.answer]);
        if (out.trimEnd() !== want) bad(`${at} 실행 출력이 정답과 달라요\n    출력: ${JSON.stringify(out.trimEnd())}\n    정답: ${JSON.stringify(want)}`);
        q.choices.forEach((ch, k) => { if (k !== q.answer && norm(ch) === out.trimEnd()) bad(`${at} 오답 보기 ${k + 1}번이 실제 출력과 같아요`); });
      }
    }
  }
  if (answers.length >= 4 && new Set(answers).size === 1) bad(`정답이 모두 ${answers[0] + 1}번이에요. 자리를 섞어요`);
}
if (errs.length) {
  console.error(`check-quiz: 문제 ${errs.length}건\n` + errs.map((e) => "  " + e).join("\n"));
  process.exit(1);
}
console.log(`check-quiz: 챕터 ${nCh}개, 문제 ${nQ}개(파이썬으로 실행해 본 문제 ${nPy}개)를 확인했어요`);
