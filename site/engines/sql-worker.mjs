// SQL 실습 칸 워커. 처음 실행할 때 PGlite를 받아요(같은 사이트의 /engines/pglite/).
import { PGlite } from "./pglite/index.js";
import { makeSql } from "./sql-core.mjs";

let engine = null;
const queue = [];
let busy = false;

async function handle({ id, cell, warm }) {
  if (!engine) {
    postMessage({ type: "status", text: "loading" });
    engine = makeSql(PGlite);
  }
  if (warm) {
    await engine.run({ setup: cell?.setup, code: "" });
    return postMessage({ type: "ready" });
  }
  postMessage({ type: "status", text: "running", id });
  const r = await engine.run(cell);
  postMessage({ type: "done", id, out: r.out, rest: r.rest, status: "ok", ms: r.ms });
}

onmessage = async (e) => {
  queue.push(e.data);
  if (busy) return;
  busy = true;
  while (queue.length) {
    const job = queue.shift();
    try {
      await handle(job);
    } catch (err) {
      postMessage({ type: "fail", id: job.id, text: String(err && err.message ? err.message : err) });
    }
  }
  busy = false;
};
