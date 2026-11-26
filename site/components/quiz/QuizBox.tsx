"use client";
import { useId, useRef, useState } from "react";
import { Check, X, RotateCcw, Presentation } from "lucide-react";

export type ViewQ = { id: string; q: string; code?: string; choices: string[]; answer: number; explain: string; page: number };
export type ViewPart = { name: string; range: string; questions: ViewQ[] };

const go = (page: number) => dispatchEvent(new CustomEvent("deck-go", { detail: page }));

/** 파트 고르기 버튼과 그 파트의 문제들. 고른 답은 이 화면에만 있고 어디에도 저장하지 않아요. */
export default function QuizBox({ parts, no }: { parts: ViewPart[]; no: string }) {
  const [cur, setCur] = useState(0);
  const [picks, setPicks] = useState<Record<string, number>>({});
  const uid = useId();
  const box = useRef<HTMLDivElement>(null);
  const pickPart = (k: number) => {
    setCur(k);
    box.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    // 휴대폰에서 옆으로 밀린 파트 버튼도 보이게 해요
    const tab = document.getElementById(`${uid}-t${k}`);
    const row = tab?.parentElement;
    if (tab && row) row.scrollTo({ left: tab.offsetLeft - row.offsetLeft - 8, behavior: "smooth" });
  };
  const part = parts[cur];
  const done = part.questions.filter((q) => picks[q.id] !== undefined);
  const right = done.filter((q) => picks[q.id] === q.answer).length;
  const reset = () =>
    setPicks((p) => {
      const n = { ...p };
      part.questions.forEach((q) => delete n[q.id]);
      return n;
    });
  return (
    <div className="qz" ref={box}>
      {parts.length > 1 && (
        <div className="qz-tabs" role="tablist" aria-label={`${no} 확인 문제 파트`}>
          {parts.map((p, k) => {
            const n = p.questions.filter((q) => picks[q.id] !== undefined).length;
            return (
              <button
                key={p.name}
                type="button"
                role="tab"
                id={`${uid}-t${k}`}
                aria-selected={k === cur}
                aria-controls={`${uid}-p`}
                onClick={() => setCur(k)}
              >
                <span>{p.name}</span>
                <small>
                  {n}/{p.questions.length}
                </small>
              </button>
            );
          })}
        </div>
      )}
      <div className="qz-part" role={parts.length > 1 ? "tabpanel" : undefined} id={`${uid}-p`} aria-labelledby={parts.length > 1 ? `${uid}-t${cur}` : undefined}>
        <div className="qz-head">
          <b>{part.name}</b>
          {part.range && <span>{part.range}</span>}
        </div>
        <ol className="qz-list">
          {part.questions.map((q, k) => (
            <Question key={q.id} q={q} n={k + 1} pick={picks[q.id]} onPick={(c) => setPicks((p) => ({ ...p, [q.id]: c }))} />
          ))}
        </ol>
        <div className="qz-foot" aria-live="polite">
          {done.length === part.questions.length ? (
            <span className="qz-score">
              {part.questions.length}문제 중 <b>{right}개</b> 맞혔어요.
              {right === part.questions.length ? " 이 파트는 다 이해했어요." : " 틀린 문제는 다시 보기로 그 쪽을 열어 보세요."}
            </span>
          ) : (
            <span className="qz-score muted">
              {part.questions.length}문제 중 {done.length}개 풀었어요.
            </span>
          )}
          <span className="qz-btns">
            {done.length > 0 && (
              <button type="button" onClick={reset}>
                <RotateCcw aria-hidden="true" />
                다시 풀기
              </button>
            )}
            {done.length === part.questions.length && cur < parts.length - 1 && (
              <button type="button" className="pri" onClick={() => pickPart(cur + 1)}>
                다음 파트
              </button>
            )}
          </span>
        </div>
      </div>
    </div>
  );
}

function Question({ q, n, pick, onPick }: { q: ViewQ; n: number; pick?: number; onPick: (c: number) => void }) {
  const answered = pick !== undefined;
  const ok = pick === q.answer;
  return (
    <li className="qz-q">
      <div className="qz-ask">
        <span className="qz-n">{n}</span>
        <p dangerouslySetInnerHTML={{ __html: q.q }} />
      </div>
      {q.code && (
        <pre className="qz-code">
          <code>{q.code}</code>
        </pre>
      )}
      <div className="qz-choices" role="group" aria-label={`${n}번 문제 보기`}>
        {q.choices.map((c, k) => {
          const state = !answered ? "" : k === q.answer ? "ok" : k === pick ? "no" : "dim";
          return (
            <button key={k} type="button" className={`qz-c ${state}`} aria-pressed={pick === k} disabled={answered} onClick={() => onPick(k)}>
              <span className="qz-k" aria-hidden="true">
                {state === "ok" ? <Check /> : state === "no" ? <X /> : k + 1}
              </span>
              <span className="qz-t" dangerouslySetInnerHTML={{ __html: c }} />
              {state === "ok" && <span className="sr-only">정답</span>}
              {state === "no" && <span className="sr-only">고른 답, 오답</span>}
            </button>
          );
        })}
      </div>
      {answered && (
        <div className={`qz-fb ${ok ? "ok" : "no"}`} role="status">
          <b>{ok ? "맞았어요" : `아쉬워요. 정답은 ${q.answer + 1}번이에요`}</b>
          <p dangerouslySetInnerHTML={{ __html: q.explain }} />
          <button type="button" className={ok ? "" : "pri"} onClick={() => go(q.page)}>
            <Presentation aria-hidden="true" />
            {q.page}쪽 {ok ? "보기" : "다시 보기"}
          </button>
        </div>
      )}
    </li>
  );
}
