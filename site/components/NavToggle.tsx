"use client";
import { useEffect, useState } from "react";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";

const narrow = () => window.matchMedia("(max-width: 900px)").matches;

/** 넓은 화면에서는 왼쪽 메뉴를 접고 펴고, 좁은 화면에서는 서랍처럼 열고 닫아요. */
export default function NavToggle() {
  const [open, setOpen] = useState(true);
  useEffect(() => {
    const d = document.documentElement;
    const sync = () => setOpen(narrow() ? d.dataset.drawer === "open" : d.dataset.nav !== "closed");
    sync();
    const mo = new MutationObserver(sync);
    mo.observe(d, { attributes: true, attributeFilter: ["data-nav", "data-drawer"] });
    window.addEventListener("resize", sync);
    return () => {
      mo.disconnect();
      window.removeEventListener("resize", sync);
    };
  }, []);
  const toggle = () => {
    const d = document.documentElement;
    if (narrow()) {
      if (d.dataset.drawer === "open") delete d.dataset.drawer;
      else d.dataset.drawer = "open";
      return;
    }
    const closed = d.dataset.nav !== "closed";
    if (closed) d.dataset.nav = "closed";
    else delete d.dataset.nav;
    try {
      localStorage.setItem("nav", closed ? "closed" : "open");
    } catch {}
  };
  return (
    <button className="icon-btn" type="button" onClick={toggle} aria-label={open ? "메뉴 접기" : "메뉴 펴기"} aria-expanded={open}>
      {open ? <PanelLeftClose className="i" /> : <PanelLeftOpen className="i" />}
    </button>
  );
}
