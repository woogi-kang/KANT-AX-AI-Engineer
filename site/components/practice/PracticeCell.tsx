"use client";
import { useEffect, useRef, useState } from "react";
import { Play, RotateCcw, Square, GitCompareArrows, LoaderCircle, Check, TriangleAlert, Presentation } from "lucide-react";
import Editor from "./Editor";
import { engine, jobOf, practiceData, type Kind, type Status } from "./engine";

export type ViewCell = { id: string; code: string; expect: string[]; page?: number; title?: string; diff?: string; err?: boolean; cut?: number };

const norm = (a: string[]) => {
  const b = a.map((l) => l.replace(/\s+$/, "").replace(/ at 0x[0-9a-f]+/g, " at 0x…"));
  while (b.length && b[b.length - 1] === "") b.pop();
  return b;
};
const MAX_SHOW = 400;

/** 두 출력에서 서로 짝이 없는 줄을 표시해요(가장 긴 공통 줄 순서, LCS). */
function lcsMarks(a: string[], b: string[]) {
  const A = a.slice(0, MAX_SHOW);
  const B = b.slice(0, MAX_SHOW);
  const n = A.length;
  const m = B.length;
  const t: number[][] = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
  for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) t[i][j] = A[i] === B[j] ? t[i + 1][j + 1] + 1 : Math.max(t[i + 1][j], t[i][j + 1]);
  const ma = new Array(n).fill(true);
  const mb = new Array(m).fill(true);
  let i = 0;
  let j = 0;
  while (i < n && j < m) {
    if (A[i] === B[j]) {
      ma[i++] = false;
      mb[j++] = false;
    } else if (t[i + 1][j] >= t[i][j + 1]) i++;
    else j++;
  }
  return { ma, mb };
}
const isErr = (l: string, kind: Kind) => (kind === "sql" ? /^(ERROR|DETAIL|HINT|LINE \d+|\s+\^$)/.test(l) : /^[A-Z]\w*(Error|Exception|Interrupt)\b/.test(l));

function Lines({ lines, kind, marks, label }: { lines: string[]; kind: Kind; marks?: boolean[]; label: string }) {
  const shown = lines.slice(0, MAX_SHOW);
  return (
    <pre className="pc-out" tabIndex={0} aria-label={label}>
      {shown.map((l, i) => (
        <span key={i} className={`${isErr(l, kind) ? "e" : ""}${marks?.[i] ? " d" : ""}`}>
          {l}
          {"\n"}
        </span>
      ))}
      {lines.length > MAX_SHOW && <span className="more-lines">… {(lines.length - MAX_SHOW).toLocaleString()}줄 더</span>}
    </pre>
  );
}

const STATUS: Record<string, string> = {
  loading: "엔진을 받고 있어요",
  packages: "패키지를 받고 있어요",
  running: "실행하고 있어요",
};

export default function PracticeCell({ dir, kind, cell, size }: { dir: string; kind: Kind; cell: ViewCell; size: string }) {
  const [code, setCode] = useState(cell.code);
  const [ver, setVer] = useState(0);
  const [out, setOut] = useState<string[] | null>(null);
  const [state, setState] = useState<"idle" | "busy" | "done">("idle");
  const [note, setNote] = useState("");
  const [cmp, setCmp] = useState(false);
  const [eng, setEng] = useState<Status>("idle");
  const live = useRef("");

  useEffect(() => engine(kind).on(setEng), [kind]);

  const warm = () => {
    const e = engine(kind);
    if (e.status === "idle") practiceData(dir).then((d) => e.warm({ setup: d.setup, packages: d.packages })).catch(() => {});
  };

  const run = async () => {
    if (state === "busy") return;
    setState("busy");
    setNote("");
    live.current = "";
    setOut([]);
    try {
      const data = await practiceData(dir);
      const r = await engine(kind).run(jobOf(data, cell.id, code), (s) => {
        live.current += s;
        setOut(live.current.replace(/\n$/, "").split("\n"));
      });
      if (r.status === "fail") {
        setOut([]);
        setNote(`실행하지 못했어요: ${r.text ?? ""}`);
      } else if (r.status === "stopped") {
        setNote("멈췄어요. 다시 실행하면 엔진을 새로 띄워요.");
        setOut(live.current ? live.current.replace(/\n$/, "").split("\n") : []);
      } else {
        setOut(r.out);
        if (r.status === "long") setNote("출력이 3,000줄을 넘어서 멈췄어요.");
        if (r.rest) setNote("끝에 ;가 없어서 마지막 문장은 아직 실행하지 않았어요. psql도 ;를 칠 때까지 기다려요.");
      }
    } catch (e) {
      setNote(String((e as Error).message ?? e));
    }
    setState("done");
  };

  const reset = () => {
    setCode(cell.code);
    setVer((v) => v + 1);
    setOut(null);
    setNote("");
    setState("idle");
  };

  const mine = out ? norm(out) : null;
  const cls = norm(cell.expect);
  const same = mine && state === "done" ? mine.length === cls.length && mine.every((l, i) => l === cls[i]) : null;
  const lm = mine && cmp && state === "done" ? lcsMarks(mine, cls) : null;
  const marksMine = lm?.ma;
  const marksCls = lm?.mb;
  const busy = state === "busy";
  const label = cell.title ? `${cell.page}쪽 ${cell.title}` : "실습 코드";

  return (
    <article className="pc" id={`p-${cell.id}`} data-state={state}>
      <header className="pc-h">
        {cell.page ? (
          <button type="button" className="pc-pg" onClick={() => dispatchEvent(new CustomEvent("deck-go", { detail: cell.page }))} aria-label={`${cell.page}쪽 슬라이드 열기`}>
            <Presentation aria-hidden="true" />
            {cell.page}쪽
          </button>
        ) : null}
        <h3>{cell.title}</h3>
        {cell.err && <span className="pc-tag">오류 예시</span>}
      </header>
      <Editor value={code} lang={kind} label={`${label} 코드 칸`} onChange={setCode} onRun={run} onFocus={warm} version={ver} />
      <div className="pc-bar">
        {busy ? (
          <button type="button" className="btn" onClick={() => engine(kind).stop()}>
            <Square aria-hidden="true" />
            멈추기
          </button>
        ) : (
          <button type="button" className="btn pri" onClick={run} onPointerEnter={warm} onFocus={warm}>
            <Play aria-hidden="true" />
            실행
          </button>
        )}
        <button type="button" className="btn" onClick={reset} disabled={busy || (code === cell.code && out === null)}>
          <RotateCcw aria-hidden="true" />
          처음으로
        </button>
        <button type="button" className="btn" aria-pressed={cmp} onClick={() => setCmp((v) => !v)}>
          <GitCompareArrows aria-hidden="true" />
          <span className="wide">수업 출력과 </span>비교
        </button>
        <span className="pc-st" aria-live="polite">
          {busy && (
            <>
              <LoaderCircle className="spin" aria-hidden="true" />
              {STATUS[eng] ?? STATUS.running}
              {eng === "loading" ? ` (처음 한 번, 약 ${size})` : ""}
            </>
          )}
          {same === true && (
            <span className="ok">
              <Check aria-hidden="true" />
              수업 출력과 같아요
            </span>
          )}
          {same === false && (
            <span className="warn">
              <TriangleAlert aria-hidden="true" />
              수업 출력과 달라요
            </span>
          )}
        </span>
      </div>
      {cell.diff && <p className="pc-diff">{cell.diff}</p>}
      {note && <p className="pc-note">{note}</p>}
      {(out !== null || cmp) && (
        <div className={`pc-res${cmp ? " two" : ""}`}>
          {out !== null && (
            <div>
              {cmp && <small>내 출력</small>}
              {out.length || busy ? <Lines lines={out} kind={kind} marks={marksMine} label="내 출력" /> : <pre className="pc-out empty">(출력 없음)</pre>}
            </div>
          )}
          {cmp && (
            <div>
              <small>수업 출력{cell.cut ? ` (앞 ${cell.expect.length.toLocaleString()}줄)` : ""}</small>
              {cls.length ? <Lines lines={cell.expect} kind={kind} marks={marksCls} label="수업 출력" /> : <pre className="pc-out empty">(출력 없음)</pre>}
            </div>
          )}
        </div>
      )}
    </article>
  );
}
