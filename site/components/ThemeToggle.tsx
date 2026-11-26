"use client";
import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

/** 밝게와 어둡게를 바꿔요. 처음에는 밝게예요. */
export default function ThemeToggle() {
  const [dark, setDark] = useState(false);
  useEffect(() => {
    const d = document.documentElement;
    setDark(d.dataset.theme === "dark" || (!d.dataset.theme && matchMedia("(prefers-color-scheme: dark)").matches));
  }, []);
  const toggle = () => {
    const next = dark ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem("theme", next);
    } catch {}
    setDark(!dark);
  };
  return (
    <button className="icon-btn" type="button" onClick={toggle} aria-label={dark ? "밝은 화면으로" : "어두운 화면으로"} title={dark ? "밝게" : "어둡게"}>
      {dark ? <Sun className="i" /> : <Moon className="i" />}
    </button>
  );
}
