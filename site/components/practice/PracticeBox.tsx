"use client";
import { useState } from "react";
import PracticeCell, { type ViewCell } from "./PracticeCell";
import ReplayCell, { type ReplayView } from "./ReplayCell";
import type { Kind } from "./engine";

export type PartView = { name: string; cells: (ViewCell | ReplayView)[] };

/** 파트 고르기 버튼과 그 파트의 실습 칸들 */
export default function PracticeBox({ dir, kind, parts, size }: { dir: string; kind: Kind | "replay"; parts: PartView[]; size: string }) {
  const [pick, setPick] = useState(0);
  const [all, setAll] = useState(false);
  const part = parts[pick];
  const FIRST = 4; // 처음에는 몇 칸만 보여 주고 나머지는 더 보기로
  const list = all ? part.cells : part.cells.slice(0, FIRST);
  return (
    <>
      {parts.length > 1 && (
        <div className="fchips pc-parts" role="tablist" aria-label="파트 고르기">
          {parts.map((p, i) => (
            <button key={p.name} type="button" role="tab" aria-selected={i === pick} aria-pressed={i === pick} onClick={() => {
                setPick(i);
                setAll(false);
              }}
            >
              {p.name}
              <span className="muted"> {p.cells.length}</span>
            </button>
          ))}
        </div>
      )}
      <div className="pc-list" role="tabpanel">
        {list.map((c) =>
          kind === "replay" ? (
            <ReplayCell key={c.id} cell={c as ReplayView} />
          ) : (
            <PracticeCell key={c.id} dir={dir} kind={kind} cell={c as ViewCell} size={size} />
          )
        )}
      </div>
      {part.cells.length > list.length && (
        <button type="button" className="btn pc-more" onClick={() => setAll(true)}>
          실습 칸 {part.cells.length - list.length}개 더 보기
        </button>
      )}
    </>
  );
}
