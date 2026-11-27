"use client";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { ChevronDown } from "lucide-react";
import NavLink from "./NavLink";

const KEY = "side-fold";
function readSaved(): Record<string, boolean> {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "{}");
  } catch {
    return {};
  }
}

/**
 * 목차에서 펼치고 접는 묶음(강의 단계처럼 아래 항목이 많은 곳).
 * 이름을 누르면 그 화면으로 가고, 오른쪽 화살표 단추로 아래 목록을 펼치거나 접어요.
 * 지금 화면이 든 묶음은 저절로 열려요. 직접 펼치거나 접은 상태는 이 브라우저에만 남아요(localStorage).
 */
export default function NavFold({ id, href, head, hrefs, count, children }: { id: string; href: string; head: React.ReactNode; hrefs: string[]; count: number; children: React.ReactNode }) {
  const p = usePathname() || "/";
  const q = p.endsWith("/") ? p : p + "/";
  const here = hrefs.includes(q);
  const [open, setOpen] = useState(here);
  useEffect(() => {
    const saved = readSaved()[id];
    setOpen(here || saved === true);
  }, [here, id]);
  const toggle = () => {
    const next = !open;
    setOpen(next);
    try {
      const s = readSaved();
      s[id] = next;
      localStorage.setItem(KEY, JSON.stringify(s));
    } catch {}
  };
  const box = `fold-${id}`;
  return (
    <div className={`fold${open ? " open" : ""}${here ? " here" : ""}`}>
      <div className="fold-h">
        <NavLink href={href}>{head}</NavLink>
        <button type="button" aria-expanded={open} aria-controls={box} aria-label={`${open ? "접기" : "펼치기"}, ${count}개`} onClick={toggle}>
          <span className="fold-n">{count}</span>
          <ChevronDown aria-hidden="true" />
        </button>
      </div>
      <div className="sub" id={box} hidden={!open}>
        {children}
      </div>
    </div>
  );
}
