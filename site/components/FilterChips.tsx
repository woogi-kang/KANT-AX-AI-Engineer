"use client";
import { useEffect, useState } from "react";

type Opt = { value: string; label: string; icon?: React.ReactNode; count?: number };

/**
 * 거르기 버튼 줄. target 안에서 data-f 값이 고른 값과 다른 칸을 숨겨요.
 * data-f에는 값을 여러 개 띄어 쓸 수 있어요(예: "KR operation"). 고른 값은 주소 뒤 ?키=값에 남아서 링크로 나눌 수 있어요.
 */
export default function FilterChips({ target, options, all = "전체", param = "f", label }: { target: string; options: Opt[]; all?: string; param?: string; label: string }) {
  const [v, setV] = useState("all");
  useEffect(() => {
    const q = new URLSearchParams(location.search).get(param);
    if (q && options.some((o) => o.value === q)) setV(q);
  }, [param, options]);
  useEffect(() => {
    const box = document.querySelector(target);
    if (!box) return;
    let shown = 0;
    box.querySelectorAll<HTMLElement>("[data-f]").forEach((el) => {
      const ok = v === "all" || (el.dataset.f ?? "").split(" ").includes(v);
      el.hidden = !ok;
      if (ok) shown++;
    });
    box.setAttribute("data-shown", String(shown));
    const u = new URL(location.href);
    if (v === "all") u.searchParams.delete(param);
    else u.searchParams.set(param, v);
    history.replaceState(history.state, "", u);
  }, [v, target, param]);
  const total = options.reduce((a, o) => a + (o.count ?? 0), 0);
  return (
    <div className="fchips" role="group" aria-label={label}>
      <button type="button" aria-pressed={v === "all"} onClick={() => setV("all")}>
        {all}
        {total ? ` ${total}` : ""}
      </button>
      {options.map((o) => (
        <button key={o.value} type="button" aria-pressed={v === o.value} onClick={() => setV(o.value)}>
          {o.icon}
          {o.label}
          {o.count !== undefined ? <span className="muted"> {o.count}</span> : null}
        </button>
      ))}
    </div>
  );
}
