"use client";
import { useEffect, useState } from "react";
import { Search, X } from "lucide-react";

/** 용어 거르기(가나다, 영문)와 용어 안 찾기. #glo 안의 [data-g] 칸을 숨기고 보여요. */
export default function GlossaryTools({ counts }: { counts: { all: number; ko: number; en: number } }) {
  const [f, setF] = useState<"all" | "ko" | "en">("all");
  const [q, setQ] = useState("");
  const [shown, setShown] = useState(counts.all);
  useEffect(() => {
    const s = new URLSearchParams(location.search);
    const g = s.get("g");
    if (g === "ko" || g === "en") setF(g);
    const qq = s.get("q");
    if (qq) setQ(qq);
  }, []);
  useEffect(() => {
    const words = q.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let n = 0;
    document.querySelectorAll<HTMLElement>("#glo [data-g]").forEach((el) => {
      const text = (el.dataset.q ?? "").toLowerCase();
      const ok = (f === "all" || el.dataset.g === f) && words.every((w) => text.includes(w));
      el.hidden = !ok;
      if (ok) n++;
    });
    setShown(n);
    const u = new URL(location.href);
    if (f === "all") u.searchParams.delete("g");
    else u.searchParams.set("g", f);
    if (q.trim()) u.searchParams.set("q", q.trim());
    else u.searchParams.delete("q");
    history.replaceState(history.state, "", u);
  }, [f, q]);
  const opts = [
    ["all", "전체", counts.all],
    ["ko", "가나다", counts.ko],
    ["en", "영문", counts.en],
  ] as const;
  return (
    <div className="gl-tools">
      <label className="gl-find">
        <Search aria-hidden="true" />
        <span className="sr-only">용어 안에서 찾기</span>
        <input type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="용어, 뜻, 질문에서 찾기" enterKeyHint="search" />
        {q && (
          <button type="button" className="icon-btn" onClick={() => setQ("")} aria-label="지우기">
            <X />
          </button>
        )}
      </label>
      <div className="fchips" role="group" aria-label="용어 거르기">
        {opts.map(([v, l, c]) => (
          <button key={v} type="button" aria-pressed={f === v} onClick={() => setF(v)}>
            {l}
            <span className="muted"> {c}</span>
          </button>
        ))}
      </div>
      <p className="gl-count" aria-live="polite">
        {shown === 0 ? "맞는 용어가 없어요. 다른 말로 찾아 보세요." : `${shown}개`}
      </p>
    </div>
  );
}
