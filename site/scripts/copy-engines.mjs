// 실습 칸 엔진과 데이터를 public/에 복사해요(빌드와 dev 전에 실행).
//  - engines/*.mjs              → public/engines/
//  - Pyodide 코어(npm pyodide)   → public/engines/pyodide/
//  - PGlite(npm @electric-sql/pglite) → public/engines/pglite/
//  - 챕터 폴더의 practice.json   → public/practice/<폴더>.json
// 엔진은 CDN 대신 같은 사이트에서 내보내요. 학교나 회사 망에서 CDN이 막혀도 돌아가고, 버전이 이 레포의 package.json에 묶여요.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const SITE = path.resolve(import.meta.dirname, "..");
const ROOT = path.resolve(SITE, "..");
const PUB = path.join(SITE, "public");
const nm = (p) => path.join(SITE, "node_modules", p);

function copy(from, to) {
  fs.mkdirSync(path.dirname(to), { recursive: true });
  fs.copyFileSync(from, to);
}
for (const d of ["engines", "practice"]) fs.rmSync(path.join(PUB, d), { recursive: true, force: true });

for (const f of fs.readdirSync(path.join(SITE, "engines"))) if (f.endsWith(".mjs")) copy(path.join(SITE, "engines", f), path.join(PUB, "engines", f));

const PY = ["pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"];
for (const f of PY) copy(nm(`pyodide/${f}`), path.join(PUB, "engines/pyodide", f));
// 실습에서 쓰는 패키지(numpy, pandas 등)와 그 패키지가 기대는 패키지의 휠도 같은 사이트에 둬요.
// .pyodide-packages/에 없으면 Pyodide 공식 CDN에서 한 번 받아 두고, 잠금 파일의 sha256과 맞는지 봐요.
const lock = JSON.parse(fs.readFileSync(nm("pyodide/pyodide-lock.json"), "utf8"));
const pyVer = JSON.parse(fs.readFileSync(nm("pyodide/package.json"), "utf8")).version;
const want = new Set();
for (const d of fs.readdirSync(ROOT)) {
  const p = path.join(ROOT, d, "practice.json");
  if (!/^\d\d-/.test(d) || !fs.existsSync(p)) continue;
  const stack = [...(JSON.parse(fs.readFileSync(p, "utf8")).packages ?? [])];
  while (stack.length) {
    const n = stack.pop();
    if (want.has(n)) continue;
    if (!lock.packages[n]) throw new Error(`Pyodide에 없는 패키지예요: ${n}`);
    want.add(n);
    stack.push(...lock.packages[n].depends);
  }
}
const cache = path.join(SITE, ".pyodide-packages");
for (const n of want) {
  const { file_name: f, sha256 } = lock.packages[n];
  const local = path.join(cache, f);
  if (!fs.existsSync(local)) {
    const url = `https://cdn.jsdelivr.net/pyodide/v${pyVer}/full/${f}`;
    const r = await fetch(url);
    if (!r.ok) throw new Error(`${url} 받기 실패 ${r.status}`);
    fs.mkdirSync(cache, { recursive: true });
    fs.writeFileSync(local, Buffer.from(await r.arrayBuffer()));
  }
  const got = crypto.createHash("sha256").update(fs.readFileSync(local)).digest("hex");
  if (got !== sha256) throw new Error(`${f}의 sha256이 잠금 파일과 달라요`);
  copy(local, path.join(PUB, "engines/pyodide", f));
}

const PG = nm("@electric-sql/pglite/dist");
for (const f of fs.readdirSync(PG)) if (/\.(js|wasm|data)$/.test(f)) copy(path.join(PG, f), path.join(PUB, "engines/pglite", f));

let n = 0;
for (const d of fs.readdirSync(ROOT)) {
  const p = path.join(ROOT, d, "practice.json");
  if (/^\d\d-/.test(d) && fs.existsSync(p)) {
    const data = JSON.parse(fs.readFileSync(p, "utf8"));
    // 화면에서 실행할 때 쓰는 것만(앞 칸 코드, 준비 SQL). 수업 출력은 화면에 이미 있어요.
    const slim = { kind: data.kind, setup: data.setup, packages: data.packages, prompt: data.prompt, cells: data.cells.map((c) => ({ id: c.id, chain: c.chain, code: c.code, noseed: c.noseed })) };
    fs.mkdirSync(path.join(PUB, "practice"), { recursive: true });
    fs.writeFileSync(path.join(PUB, "practice", `${d}.json`), JSON.stringify(slim));
    n++;
  }
}
console.log(`copy-engines: 엔진 복사, 파이썬 패키지 ${want.size}개, 실습 데이터 ${n}개`);
