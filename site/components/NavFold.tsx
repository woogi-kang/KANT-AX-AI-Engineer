"use client";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { ChevronDown } from "lucide-react";

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
 * 줄 전체가 단추예요. 닫힌 묶음을 누르면 펼치면서 첫 항목(href)으로 가요. 지금 화면이 든 묶음은 펼치기만 하고, 열린 묶음을 누르면 접혀요.
 * 묶음 전체를 한눈에 보는 화면은 "전체 강의"에만 있어요.
 * 지금 화면이 든 묶음은 저절로 열려요. 직접 펼치거나 접은 상태는 이 브라우저에만 남아요(localStorage).
 */
export default function NavFold({ id, href, head, hrefs, count, children }: { id: string; href: string; head: React.ReactNode; hrefs: string[]; count: number; children: React.ReactNode }) {
  const p = usePathname() || "/";
  const q = p.endsWith("/") ? p : p + "/";
  const here = hrefs.includes(q);
  const router = useRouter();
  const [open, setOpen] = useState(here);
  // 첫 항목 화면을 미리 받아 둬서 단계 이름을 누르면 바로 넘어가요(챕터 링크가 화면에 보일 때 받는 것과 같아요)
  useEffect(() => {
    if (!here) router.prefetch(href);
  }, [here, href, router]);
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
    if (next && !here) router.push(href);
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
        {children}
      </div>
    </div>
  );
}
