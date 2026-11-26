"use client";
import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

/** 밝은 화면과 어두운 화면을 바꿔요. 처음에는 밝은 화면이고, 고른 것은 이 브라우저에 남겨요. */
export default function ThemeToggle() {
  const [dark, setDark] = useState(false);
  useEffect(() => setDark(document.documentElement.dataset.theme === "dark"), []);
  const toggle = () => {
    const next = dark ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem("theme", next);
    } catch {}
    setDark(!dark);
  };
  const label = dark ? "밝은 화면으로 바꾸기" : "어두운 화면으로 바꾸기";
  return (
    <button className="icon-btn" type="button" onClick={toggle} aria-label={label} title={label}>
      {dark ? <Sun aria-hidden="true" /> : <Moon aria-hidden="true" />}
    </button>
  );
}
