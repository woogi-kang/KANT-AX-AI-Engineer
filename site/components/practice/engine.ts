"use client";
// 실습 칸이 엔진(워커)을 부르는 곳이에요. 파이썬과 SQL 워커를 하나씩만 띄워 여러 칸이 같이 써요.
// 엔진 파일은 같은 사이트의 /engines/ 에 있어요(scripts/copy-engines.mjs가 빌드 때 복사).

export type Kind = "python" | "sql";
export type Job = { prelude: string[]; code: string; setup?: string; packages?: string[]; prompt?: string };
export type Result = { out: string[]; status: "ok" | "err" | "long" | "stopped" | "fail"; ms?: number; rest?: string; text?: string };
type Listener = (s: Status) => void;
export type Status = "idle" | "loading" | "packages" | "ready" | "running";

type Pending = { resolve: (r: Result) => void; onChunk?: (s: string) => void };

class Engine {
  kind: Kind;
  worker: Worker | null = null;
  status: Status = "idle";
  listeners = new Set<Listener>();
  pending = new Map<number, Pending>();
  seq = 0;
  constructor(kind: Kind) {
    this.kind = kind;
  }
  private set(s: Status) {
    this.status = s;
    this.listeners.forEach((f) => f(s));
  }
  private ensure() {
    if (this.worker) return this.worker;
    const url = this.kind === "python" ? "/engines/py-worker.mjs" : "/engines/sql-worker.mjs";
    const w = new Worker(url, { type: "module" });
    w.onmessage = (e) => {
      const m = e.data;
      if (m.type === "status") this.set(m.text);
      else if (m.type === "ready") this.set("ready");
      else if (m.type === "chunk") this.pending.get(m.id)?.onChunk?.(m.text);
      else if (m.type === "done" || m.type === "fail") {
        const p = this.pending.get(m.id);
        this.pending.delete(m.id);
        if (!this.pending.size) this.set("ready");
        p?.resolve(m.type === "done" ? { out: m.out, status: m.status, ms: m.ms, rest: m.rest } : { out: [], status: "fail", text: m.text });
      }
    };
    w.onerror = (e) => {
      this.pending.forEach((p) => p.resolve({ out: [], status: "fail", text: e.message || "엔진을 불러오지 못했어요" }));
      this.pending.clear();
      this.worker = null;
      this.set("idle");
    };
    this.worker = w;
    return w;
  }
  /** 처음 손댈 때 미리 받아 둬요. */
  warm(job?: Partial<Job>) {
    if (this.worker) return;
    this.set("loading");
    this.ensure().postMessage({ warm: true, cell: job ?? {} });
  }
  run(job: Job, onChunk?: (s: string) => void): Promise<Result> {
    const id = ++this.seq;
    const w = this.ensure();
    return new Promise((resolve) => {
      this.pending.set(id, { resolve, onChunk });
      w.postMessage({ id, cell: job });
    });
  }
  /** 끝나지 않는 코드를 멈춰요: 워커를 끄고 다음 실행 때 다시 띄워요. */
  stop() {
    this.worker?.terminate();
    this.worker = null;
    this.pending.forEach((p) => p.resolve({ out: [], status: "stopped" }));
    this.pending.clear();
    this.set("idle");
  }
  on(f: Listener) {
    this.listeners.add(f);
    return () => {
      this.listeners.delete(f);
    };
  }
}

const engines: Partial<Record<Kind, Engine>> = {};
export function engine(kind: Kind) {
  return (engines[kind] ??= new Engine(kind));
}

type Data = { cells: { id: string; chain?: string; code?: string; noseed?: boolean }[]; setup?: string; packages?: string[]; prompt?: string };
const dataCache = new Map<string, Promise<Data>>();
/** 앞 칸과 준비 SQL이 든 practice.json(빌드 때 /practice/폴더.json으로 복사) */
export function practiceData(dir: string) {
  if (!dataCache.has(dir))
    dataCache.set(
      dir,
      fetch(`/practice/${dir}.json`).then((r) => {
        if (!r.ok) throw new Error("실습 데이터를 받지 못했어요");
        return r.json();
      })
    );
  return dataCache.get(dir)!;
}
export function jobOf(data: Data, id: string, code: string): Job {
  const cell = data.cells.find((c) => c.id === id);
  const prelude: string[] = [];
  for (const c of data.cells) {
    if (c.id === id) break;
    if (c.chain === cell?.chain && c.code) prelude.push(c.code);
  }
  return { prelude, code, setup: cell?.noseed ? undefined : data.setup, packages: data.packages, prompt: data.prompt };
}
