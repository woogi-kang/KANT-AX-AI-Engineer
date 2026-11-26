"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { MENU, menuOf } from "@/lib/site";

/** 머리글 메뉴. 지금 화면이 속한 메뉴에 aria-current를 달아요. */
export default function TopMenu() {
  const cur = menuOf(usePathname() || "/");
  return (
    <>
      {MENU.map(([k, t, h]) => (
        <Link key={k} href={h} aria-current={k === cur ? "page" : undefined}>
          {t}
        </Link>
      ))}
    </>
  );
}
