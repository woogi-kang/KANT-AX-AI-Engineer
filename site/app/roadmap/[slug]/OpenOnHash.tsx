"use client";
import { useEffect } from "react";

/** 주소 뒤 #sec-N으로 들어오면 그 접는 절을 펼쳐요. */
export default function OpenOnHash() {
  useEffect(() => {
    const open = () => {
      const el = location.hash ? document.getElementById(decodeURIComponent(location.hash.slice(1))) : null;
      if (el instanceof HTMLDetailsElement) {
        el.open = true;
        el.scrollIntoView({ block: "start" });
      }
    };
    open();
    window.addEventListener("hashchange", open);
    return () => window.removeEventListener("hashchange", open);
  }, []);
  return null;
}
