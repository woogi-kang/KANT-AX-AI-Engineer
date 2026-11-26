"use client";
import { useEffect, useRef, useState } from "react";
import { CornerDownLeft, RotateCcw, Presentation, Lightbulb, ListChecks } from "lucide-react";

export type Step = { cmd: string; out: string[]; cwd?: string; note?: string };
export type ReplayView = { id: string; page?: number; title?: string; steps: Step[]; diff?: string };

// 띄어쓰기 수와 앞뒤 빈칸은 보지 않아요.
const same = (a: string, b: string) => a.trim().replace(/\s+/g, " ") === b.trim().replace(/\s+/g, " ");

/**
 * 재생형 칸. 수강생이 친 명령이 수업 명령과 같으면, 수업에서 실제로 실행해 옮겨 둔 출력을 보여 줘요.
 * 실제로 실행하지는 않아요(터미널, Git, Docker는 브라우저에서 돌릴 수 없어서요).
 */
export default function ReplayCell({ cell }: { cell: ReplayView }) {
  const steps = cell.steps;
  const [n, setN] = useState(0); // 지나간 명령 수
  const [text, setText] = useState("");
  const [miss, setMiss] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  const screen = useRef<HTMLPreElement>(null);
  // 명령 없이 출력만 있는 단계(cmd가 빈 것)는 저절로 지나가요.
  useEffect(() => {
    if (n < steps.length && !steps[n].cmd) setN(n + 1);
  }, [n, steps]);
  useEffect(() => {
    const el = screen.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [n]);
  const cur = steps[n];
  const done = n >= steps.length;
  const prompt = (s: Step) => `${s.cwd ? s.cwd + " " : ""}$ `;

  const enter = () => {
    if (!cur) return;
    if (same(text, cur.cmd)) {
      setN(n + 1);
      setText("");
      setMiss(false);
    } else setMiss(true);
  };
  const reset = () => {
    setN(0);
    setText("");
    setMiss(false);
  };

  return (
    <article className="pc rp" id={`p-${cell.id}`}>
      <header className="pc-h">
        {cell.page ? (
          <button type="button" className="pc-pg" onClick={() => dispatchEvent(new CustomEvent("deck-go", { detail: cell.page }))} aria-label={`${cell.page}쪽 슬라이드 열기`}>
            <Presentation aria-hidden="true" />
            {cell.page}쪽
          </button>
        ) : null}
        <h3>{cell.title}</h3>
        <span className="pc-tag">
          {Math.min(n, steps.length)}/{steps.length}
        </span>
      </header>
      <pre className="rp-term" ref={screen} tabIndex={0} aria-label="터미널 화면" aria-live="polite">
        {steps.slice(0, n).map((s, i) => (
          <span key={i}>
            {s.cmd && (
              <span className="c">
                <b>{prompt(s)}</b>
                {s.cmd}
                {"\n"}
              </span>
            )}
            {s.out.map((l, j) => (
              <span key={j} className={/^#( |$)/.test(l) ? "m" : ""}>
                {l}
                {"\n"}
              </span>
            ))}
          </span>
        ))}
        {done ? (
          <span className="m">끝까지 따라 쳤어요.</span>
        ) : (
          <span className="c">
            <b>{prompt(cur)}</b>
          </span>
        )}
      </pre>
      {!done && (
        <form
          className="rp-in"
          onSubmit={(e) => {
            e.preventDefault();
            enter();
          }}
        >
          <span aria-hidden="true">$</span>
          <input
            ref={input}
            value={text}
            onChange={(e) => {
              setText(e.target.value);
              setMiss(false);
            }}
            aria-label={`명령 ${n + 1} 입력`}
            placeholder="명령을 쳐 보세요"
            autoCapitalize="off"
            autoCorrect="off"
            autoComplete="off"
            spellCheck={false}
            enterKeyHint="send"
          />
          <button type="submit" className="btn pri" aria-label="실행">
            <CornerDownLeft aria-hidden="true" />
          </button>
        </form>
      )}
      <div className="pc-bar">
        {!done && (
          <button
            type="button"
            className="btn"
            onClick={() => {
              setText(cur.cmd);
              setMiss(false);
              input.current?.focus();
            }}
          >
            <Lightbulb aria-hidden="true" />
            명령 보기
          </button>
        )}
        {!done && (
          <button type="button" className="btn" onClick={() => setN(steps.length)}>
            <ListChecks aria-hidden="true" />
            끝까지 보기
          </button>
        )}
        <button type="button" className="btn" onClick={reset} disabled={n === 0}>
          <RotateCcw aria-hidden="true" />
          처음으로
        </button>
      </div>
      {miss && cur && (
        <p className="pc-note" role="status">
          수업에서 친 명령과 달라요. 철자와 띄어쓰기를 확인해 봐요. 모르겠으면 명령 보기를 눌러요.
        </p>
      )}
      {cell.diff && <p className="pc-diff">{cell.diff}</p>}
    </article>
  );
}
