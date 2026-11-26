"use client";

/** 누르면 위 슬라이드 자리를 그 쪽으로 열어요 */
export default function PartGo({ page, className, children }: { page: number; className?: string; children: React.ReactNode }) {
  return (
    <button type="button" className={className} onClick={() => dispatchEvent(new CustomEvent("deck-go", { detail: page }))}>
      {children}
    </button>
  );
}
