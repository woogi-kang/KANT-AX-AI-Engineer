"use client";
import { useEffect, useRef, useState } from "react";
import "./study.css";

export type StudyTab = { id: string; label: string; count?: string };

/**
 * 챕터 화면 슬라이드 아래의 "공부 칸" 탭(구성, 바로 쳐 보기, 확인 문제, 교안).
 * 모든 칸은 HTML에 다 들어 있고, 고른 탭만 보여요(.study[data-active] + [data-panel]).
 * 주소 #탭 이름이나 #교안 절 이름(예: 명령어 요약 버튼)으로 오면 그 탭과 그 절을 열어요.
 */
export default function StudyTabs({ tabs, children }: { tabs: StudyTab[]; children: React.ReactNode }) {
  const [active, setActive] = useState(tabs[0].id);
  const root = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const go = (scroll: boolean) => {
      const id = decodeURIComponent(location.hash.slice(1));
      if (!id) return;
      if (tabs.some((t) => t.id === id)) {
        setActive(id);
        if (scroll) requestAnimationFrame(() => root.current?.scrollIntoView({ block: "start" }));
        return;
      }
      const el = document.getElementById(id);
      if (!el || !root.current?.contains(el)) return;
      const panel = el.closest<HTMLElement>("[data-panel]")?.dataset.panel ?? (el.dataset.panel || null);
      if (panel) setActive(panel);
      if (scroll) requestAnimationFrame(() => root.current?.scrollIntoView({ block: "start" }));
    };
    go(true);
    const on = () => go(true);
    addEventListener("hashchange", on);
    return () => removeEventListener("hashchange", on);
  }, [tabs]);

  const choose = (id: string) => {
    setActive(id);
    history.replaceState(history.state, "", id === tabs[0].id ? location.pathname + location.search : `#${id}`);
    const top = root.current?.getBoundingClientRect().top ?? 0;
    if (top < 0) root.current?.scrollIntoView({ block: "start" });
  };
  return (
    <div className="study" data-active={active} ref={root} id="study">
      <div className="study-bar" role="tablist" aria-label="공부 칸">
        {tabs.map((t) => (
          <button key={t.id} type="button" role="tab" id={`tab-${t.id}`} aria-selected={active === t.id} aria-controls={`panel-${t.id}`} onClick={() => choose(t.id)}>
            {t.label}
            {t.count && <span className="study-n">{t.count}</span>}
          </button>
        ))}
      </div>
      {children}
    </div>
  );
}
