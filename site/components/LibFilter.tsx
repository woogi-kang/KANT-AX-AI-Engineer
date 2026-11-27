"use client";
import { useEffect, useMemo, useState } from "react";
import { Search, X } from "lucide-react";

export type LibOpt = { value: string; label: string; icon?: React.ReactNode; count?: number };
export type LibGroup = {
  /** 주소 뒤 ?키=값의 키이자, 칸의 data-키 이름 */
  key: string;
  label: string;
  options: LibOpt[];
  /** chips: 버튼 줄, select: 고르기 상자(값이 많을 때) */
  kind?: "chips" | "select";
};

/**
 * 사례와 자료 화면의 거르기. 거르기 묶음 여러 개와 찾기 칸을 같이 써요(모두 맞는 칸만 보여요).
 * target 안의 칸에는 data-<키>="값 값"과 찾을 글자 data-q를 달아요.
 * 고른 값은 주소 뒤 ?키=값에 남아서 링크로 나눌 수 있어요.
 */
export default function LibFilter({ target, groups, search, unit = "개" }: { target: string; groups: LibGroup[]; search?: string; unit?: string }) {
  const empty = useMemo(() => Object.fromEntries(groups.map((g) => [g.key, "all"])), [groups]);
  const [v, setV] = useState<Record<string, string>>(empty);
  const [q, setQ] = useState("");
  const [shown, setShown] = useState<number | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const sp = new URLSearchParams(location.search);
    const next: Record<string, string> = {};
    for (const g of groups) {
      const x = sp.get(g.key);
      next[g.key] = x && g.options.some((o) => o.value === x) ? x : "all";
    }
    setV(next);
    setQ(sp.get("q") ?? "");
  }, [groups]);

  useEffect(() => {
    const box = document.querySelector(target);
    if (!box) return;
    const items = box.querySelectorAll<HTMLElement>("[data-item]");
    const words = q.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let n = 0;
    items.forEach((el) => {
      const ok =
        groups.every((g) => v[g.key] === "all" || (el.dataset[g.key] ?? "").split(" ").includes(v[g.key])) &&
        words.every((w) => (el.dataset.q ?? el.textContent ?? "").toLowerCase().includes(w));
      el.hidden = !ok;
      if (ok) n++;
    });
    setShown(n);
    setTotal(items.length);
    box.setAttribute("data-shown", String(n));
    const u = new URL(location.href);
    for (const g of groups) {
      if (v[g.key] === "all") u.searchParams.delete(g.key);
      else u.searchParams.set(g.key, v[g.key]);
    }
    if (q.trim()) u.searchParams.set("q", q.trim());
    else u.searchParams.delete("q");
    history.replaceState(history.state, "", u);
  }, [v, q, target, groups]);

  const set = (k: string, x: string) => setV((o) => ({ ...o, [k]: x }));
  const dirty = q.trim() !== "" || groups.some((g) => v[g.key] !== "all");

  return (
    <div className="lf">
      {search && (
        <label className="lf-q">
          <Search aria-hidden="true" />
          <input type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder={search} aria-label={search} />
        </label>
      )}
      {groups
        .filter((g) => g.kind !== "select")
        .map((g) => (
          <div key={g.key} className="lf-row">
            <span className="lf-l">{g.label}</span>
            <div className="fchips" role="group" aria-label={g.label}>
              <button type="button" aria-pressed={v[g.key] === "all"} onClick={() => set(g.key, "all")}>
                전체
              </button>
              {g.options.map((o) => (
                <button key={o.value} type="button" aria-pressed={v[g.key] === o.value} onClick={() => set(g.key, o.value)}>
                  {o.icon}
                  {o.label}
                  {o.count !== undefined ? <span className="lf-n"> {o.count}</span> : null}
                </button>
              ))}
            </div>
          </div>
        ))}
      {groups.some((g) => g.kind === "select") && (
        <div className="lf-sels">
          {groups
            .filter((g) => g.kind === "select")
            .map((g) => (
              <label key={g.key} className={v[g.key] !== "all" ? "lf-sel on" : "lf-sel"}>
                <span>{g.label}</span>
                <select value={v[g.key]} onChange={(e) => set(g.key, e.target.value)}>
                  <option value="all">전체</option>
                  {g.options.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                      {o.count !== undefined ? ` (${o.count})` : ""}
                    </option>
                  ))}
                </select>
              </label>
            ))}
        </div>
      )}
      <div className="lf-st" aria-live="polite">
        {shown !== null && (
          <span>
            {shown === total ? `${total}${unit}` : `${total}${unit} 중 ${shown}${unit}`}
            {shown === 0 && " · 맞는 자료가 없어요"}
          </span>
        )}
        {dirty && (
          <button
            type="button"
            className="lf-x"
            onClick={() => {
              setV(empty);
              setQ("");
            }}
          >
            <X aria-hidden="true" />
            필터 초기화
          </button>
        )}
      </div>
    </div>
  );
}
