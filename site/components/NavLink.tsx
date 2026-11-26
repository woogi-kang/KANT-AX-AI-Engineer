"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

/** 지금 화면이면 aria-current를 다는 링크. exact가 아니면 하위 주소에서도 켜져요. */
export default function NavLink({ href, exact = true, className, children, onClick }: { href: string; exact?: boolean; className?: string; children: React.ReactNode; onClick?: () => void }) {
  const p = usePathname() || "/";
  const here = exact ? p === href || p + "/" === href : p.startsWith(href);
  return (
    <Link href={href} className={className} aria-current={here ? "page" : undefined} onClick={onClick}>
      {children}
    </Link>
  );
}
