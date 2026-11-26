// 파이썬 실습 칸 워커. 처음 실행할 때 Pyodide를 받아요(같은 사이트의 /engines/pyodide/).
import { loadPyodide } from "./pyodide/pyodide.mjs";
import { makePython } from "./python-core.mjs";

let enginePromise = null;
const loaded = new Set();
async function ready(packages) {
  if (!enginePromise) {
    postMessage({ type: "status", text: "loading" });
    enginePromise = makePython(loadPyodide, { indexURL: new URL("./pyodide/", import.meta.url).href });
  }
  const engine = await enginePromise;
  const need = (packages || []).filter((p) => !loaded.has(p));
  if (need.length) {
    postMessage({ type: "status", text: "packages" });
    await engine.loadPackages(need);
    need.forEach((p) => loaded.add(p));
  }
  return engine;
}

onmessage = async (e) => {
  const { id, cell, warm } = e.data;
  try {
    const en = await ready(cell?.packages);
    if (warm) return postMessage({ type: "ready" });
    postMessage({ type: "status", text: "running", id });
    let pending = "";
    let timer = null;
    const flush = () => {
      if (pending) postMessage({ type: "chunk", id, text: pending });
      pending = "";
      timer = null;
    };
    const r = await en.run(cell, (s) => {
      pending += s;
      if (!timer) timer = setTimeout(flush, 30);
    });
    if (timer) clearTimeout(timer);
    postMessage({ type: "done", id, out: r.out, status: r.status, ms: r.ms });
  } catch (err) {
    postMessage({ type: "fail", id, text: String(err && err.message ? err.message : err) });
  }
};
