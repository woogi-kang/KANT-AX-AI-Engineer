"use client";
import { useEffect, useState } from "react";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";

/** 넓은 화면에서 왼쪽 목차를 접고 펼쳐요. 고른 상태는 이 브라우저에 남겨 둬요(좁은 화면은 NavToggle). */
export default function SideToggle() {
  const [closed, setClosed] = useState(false);
  useEffect(() => setClosed(document.documentElement.dataset.side === "closed"), []);
  const toggle = () => {
    const next = !closed;
    setClosed(next);
    const d = document.documentElement;
    if (next) d.dataset.side = "closed";
    else delete d.dataset.side;
    try {
      localStorage.setItem("side-closed", next ? "1" : "0");
    } catch {}
  };
  const label = closed ? "목차 펼치기" : "목차 접기";
  return (
    <button className="icon-btn side-tg" type="button" onClick={toggle} aria-label={label} title={label} aria-expanded={!closed} aria-controls="side">
      {closed ? <PanelLeftOpen aria-hidden="true" /> : <PanelLeftClose aria-hidden="true" />}
    </button>
  );
}
