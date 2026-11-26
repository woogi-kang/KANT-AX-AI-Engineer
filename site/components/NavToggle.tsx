"use client";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";

/** 좁은 화면에서 왼쪽 목차를 열고 닫아요. 화면을 옮기거나 Esc를 누르면 닫혀요. */
export default function NavToggle() {
  const [open, setOpen] = useState(false);
  const path = usePathname();
  useEffect(() => setOpen(false), [path]);
  useEffect(() => {
    const d = document.documentElement;
    if (open) d.dataset.nav = "open";
    else delete d.dataset.nav;
    const key = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    const click = (e: MouseEvent) => (e.target as HTMLElement).closest(".scrim") && setOpen(false);
    addEventListener("keydown", key);
    addEventListener("click", click);
    return () => {
      removeEventListener("keydown", key);
      removeEventListener("click", click);
    };
  }, [open]);
  return (
    <button className="icon-btn mtg" type="button" aria-label={open ? "목차 닫기" : "목차 열기"} aria-expanded={open} aria-controls="side" onClick={() => setOpen(!open)}>
      {open ? <X aria-hidden="true" /> : <Menu aria-hidden="true" />}
    </button>
  );
}
