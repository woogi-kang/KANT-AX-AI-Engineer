// 모든 실습 칸을 실제로 실행해서 수업 출력과 같은지 봐요(파이썬은 Pyodide, SQL은 PGlite).
//   node scripts/practice-check.mjs            모든 챕터
//   node scripts/practice-check.mjs 13 36      고른 챕터만
//   node scripts/practice-check.mjs --accept   다른 칸에 diff 메모를 적어 둬요(사람이 먼저 차이를 읽고 써요)
// 다른 칸은 practice.json에 "diff" 메모가 있어야 해요. 메모 없이 다르면 실패로 끝나요.
import fs from "node:fs";
import path from "node:path";
import { loadPyodide } from "pyodide";
import { PGlite } from "@electric-sql/pglite";
import { makePython } from "../engines/python-core.mjs";
import { makeSql } from "../engines/sql-core.mjs";
import { jobOf } from "../engines/practice.mjs";
import { compare } from "../engines/compare.mjs";

const ROOT = path.resolve(import.meta.dirname, "..", "..");
const args = process.argv.slice(2);
const accept = args.includes("--accept");
const verbose = args.includes("-v");
const pick = args.filter((a) => /^\d\d$/.test(a));
const dirs = fs
  .readdirSync(ROOT)
  .filter((d) => /^\d\d-/.test(d) && fs.existsSync(path.join(ROOT, d, "practice.json")))
  .filter((d) => !pick.length || pick.includes(d.slice(0, 2)))
  .sort();

let py = null;
let sql = null;
let total = 0;
let same = 0;
let noted = 0;
const bad = [];
const t0 = Date.now();

for (const d of dirs) {
  const file = path.join(ROOT, d, "practice.json");
  const data = JSON.parse(fs.readFileSync(file, "utf8"));
  if (data.kind === "replay") continue;
  let changed = false;
  for (const cell of data.cells) {
    if (cell.hidden || !cell.expect) continue;
    total++;
    const job = jobOf(data, cell);
    let r;
    if (data.kind === "python") {
      // numpy, pandas 같은 패키지: .pyodide-packages에 받아 둔 파일이 있으면 그걸 쓰고, 없으면 Pyodide 공식 CDN에서 받아요.
      const cache = path.join(import.meta.dirname, "..", ".pyodide-packages");
      py ??= await makePython(loadPyodide, fs.existsSync(cache) ? { packageCacheDir: cache } : {});
      if (data.packages) await py.loadPackages(data.packages);
      r = await py.run(job);
    } else {
      sql ??= makeSql(PGlite);
      r = await sql.run(job);
    }
    const c = compare(r.out, cell.expect);
    if (c.same) {
      same++;
      if (cell.diff && accept) {
        delete cell.diff;
        changed = true;
      }
      continue;
    }
    if (cell.diff) {
      noted++;
      continue;
    }
    bad.push({ d, cell, c });
    if (accept) {
      cell.diff = "수업 화면과 다를 수 있어요";
      changed = true;
    }
  }
  if (changed) fs.writeFileSync(file, JSON.stringify(data, null, 1) + "\n");
  console.log(`${d}: ${data.cells.filter((c) => !c.hidden).length}칸`);
}
await sql?.close();

for (const { d, cell, c } of bad) {
  console.log(`\n--- ${d} ${cell.id} (${cell.page ?? "-"}쪽) ${cell.title ?? ""}`);
  if (verbose) console.log(cell.code);
  const n = Math.max(c.a.length, c.b.length);
  let shown = 0;
  for (let i = 0; i < n; i++) {
    if (c.a[i] === c.b[i]) continue;
    if (++shown > 4) {
      console.log(`  … 줄 수 수업 ${c.b.length}, 여기 ${c.a.length}`);
      break;
    }
    console.log(`  수업 | ${c.b[i] ?? "(없음)"}`);
    console.log(`  여기 | ${c.a[i] ?? "(없음)"}`);
  }
}
console.log(`\n실습 칸 ${total}개: 같음 ${same}, 다름(메모 있음) ${noted}, 다름(메모 없음) ${bad.length}  ${((Date.now() - t0) / 1000).toFixed(1)}초`);
if (bad.length && !accept) process.exit(1);
