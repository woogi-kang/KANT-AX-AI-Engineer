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
 * 줄 전체가 단추라서 어디를 눌러도 펼치거나 접혀요. 묶음 화면으로 가는 링크는 펼친 목록 맨 위(allLabel)에 있어요.
 * 지금 화면이 든 묶음은 저절로 열려요. 직접 펼치거나 접은 상태는 이 브라우저에만 남아요(localStorage).
 */
export default function NavFold({ id, href, allLabel = "모두 보기", head, hrefs, count, children }: { id: string; href: string; allLabel?: string; head: React.ReactNode; hrefs: string[]; count: number; children: React.ReactNode }) {
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
      <button type="button" className="fold-h" aria-expanded={open} aria-controls={box} onClick={toggle}>
        <span className="fold-t">{head}</span>
        <span className="fold-n" aria-label={`${count}개`}>
          {count}
        </span>
        <ChevronDown aria-hidden="true" />
      </button>
      <div className="sub" id={box} hidden={!open}>
        <NavLink href={href} className="fold-all">
          {allLabel}
        </NavLink>
        {children}
      </div>
    </div>
  );
}
