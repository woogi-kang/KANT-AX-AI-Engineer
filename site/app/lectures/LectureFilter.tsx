"use client";
import { useEffect, useState } from "react";

type Opt = { value: string; label: string; icon?: React.ReactNode; count: number };

/**
 * 강의 목록 거르기: 분류(터미널, Git …)와 레벨(입문, 기초, 응용)을 같이 골라요.
 * #lec-list 안에서 data-track, data-level이 맞지 않는 카드를 숨기고, 카드가 하나도 안 남은 단계는 통째로 숨겨요.
 * 고른 값은 주소 뒤 ?track=…&level=…에 남아서 링크로 나눌 수 있어요.
 */
export default function LectureFilter({ tracks, levels, total }: { tracks: Opt[]; levels: Opt[]; total: number }) {
  const [track, setTrack] = useState("all");
  const [level, setLevel] = useState("all");
  const [shown, setShown] = useState(total);
  useEffect(() => {
    const q = new URLSearchParams(location.search);
    const t = q.get("track");
    const l = q.get("level");
    if (t && tracks.some((o) => o.value === t)) setTrack(t);
    if (l && levels.some((o) => o.value === l)) setLevel(l);
  }, [tracks, levels]);
  useEffect(() => {
    const box = document.getElementById("lec-list");
    if (!box) return;
    let n = 0;
    box.querySelectorAll<HTMLElement>("[data-stage]").forEach((s) => {
      let k = 0;
      s.querySelectorAll<HTMLElement>("[data-track]").forEach((el) => {
        const ok = (track === "all" || el.dataset.track === track) && (level === "all" || el.dataset.level === level);
        el.hidden = !ok;
        if (ok) k++;
      });
      s.hidden = k === 0;
      const c = s.querySelector<HTMLElement>("[data-cnt]");
      if (c) c.textContent = track === "all" && level === "all" ? (c.dataset.cnt ?? "") : `${k}챕터 보이는 중`;
      n += k;
    });
    setShown(n);
    const u = new URL(location.href);
    for (const [k, v] of [["track", track], ["level", level]] as const) {
      if (v === "all") u.searchParams.delete(k);
      else u.searchParams.set(k, v);
    }
    history.replaceState(history.state, "", u);
  }, [track, level]);
  const row = (label: string, opts: Opt[], v: string, set: (x: string) => void) => (
    <div className="fchips" role="group" aria-label={label}>
      <span className="fl">{label}</span>
      <button type="button" aria-pressed={v === "all"} onClick={() => set("all")}>
        전체
      </button>
      {opts.map((o) => (
        <button key={o.value} type="button" aria-pressed={v === o.value} onClick={() => set(v === o.value ? "all" : o.value)}>
          {o.icon}
          {o.label}
          <span className="muted"> {o.count}</span>
        </button>
      ))}
    </div>
  );
  const filtered = track !== "all" || level !== "all";
  return (
    <div className="lec-filter">
      {row("분류", tracks, track, setTrack)}
      {row("레벨", levels, level, setLevel)}
      <p className="lf-res" aria-live="polite">
        {filtered ? (
          <>
            {shown ? `${shown}챕터를 찾았어요.` : "맞는 챕터가 없어요."}{" "}
            <button
              type="button"
              onClick={() => {
                setTrack("all");
                setLevel("all");
              }}
            >
              필터 초기화
            </button>
          </>
        ) : (
          `${total}챕터 모두 보는 중이에요.`
        )}
      </p>
    </div>
  );
}
