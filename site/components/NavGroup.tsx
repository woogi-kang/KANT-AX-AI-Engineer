"use client";
import { usePathname } from "next/navigation";

/** 지금 화면이 hrefs 중 하나일 때만 아래 목록을 펼쳐요 */
export default function NavGroup({ hrefs, prefix, children }: { hrefs: string[]; prefix?: string; children: React.ReactNode }) {
  const p = usePathname() || "/";
  const q = p.endsWith("/") ? p : p + "/";
  const open = hrefs.includes(q) || (!!prefix && q.startsWith(prefix));
  if (!open) return null;
  return <div className="sub">{children}</div>;
}
