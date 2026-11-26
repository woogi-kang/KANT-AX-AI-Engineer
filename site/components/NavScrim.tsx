"use client";
import { useEffect } from "react";
import { usePathname } from "next/navigation";

/** 좁은 화면에서 서랍 메뉴 바깥을 누르거나 Esc를 치면 닫아요. 페이지를 옮겨도 닫아요. */
export default function NavScrim() {
  const pathname = usePathname();
  useEffect(() => {
    delete document.documentElement.dataset.drawer;
  }, [pathname]);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") delete document.documentElement.dataset.drawer;
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
  return <div className="nav-scrim" aria-hidden="true" onClick={() => delete document.documentElement.dataset.drawer} />;
}
