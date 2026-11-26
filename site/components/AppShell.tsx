import Link from "next/link";
import { LifeBuoy, Map, Megaphone, Scale } from "lucide-react";
import { load } from "@/lib/content";
import SiteFooter from "./SiteFooter";
import NavScrim from "./NavScrim";

type Key = "home" | "extras" | "news" | "legal";

/** 왼쪽 사이트 메뉴와 본문. 홈, 새 소식, 이용 안내가 같이 써요. */
export default function AppShell({ current, children }: { current: Key; children: React.ReactNode }) {
  const { chapters, extras } = load();
  const item = (key: Key, href: string, label: string, icon: React.ReactNode, cnt?: number) => (
    <Link href={href} aria-current={current === key ? "page" : undefined}>
      {icon}
      <span className="lbl">{label}</span>
      {cnt !== undefined && <span className="cnt">{cnt}</span>}
    </Link>
  );
  return (
    <div className="app">
      <nav className="appnav" aria-label="사이트 메뉴">
        {item("home", "/", "학습 로드맵", <Map className="i" />, chapters.length)}
        {item("extras", "/#guides", "가이드", <LifeBuoy className="i" />, extras.length)}
        <div className="sep" />
        {item("news", "/updates/", "업데이트", <Megaphone className="i" />)}
        {item("legal", "/legal/", "이용 안내", <Scale className="i" />)}
      </nav>
      <NavScrim />
      <main className="app-main" id="main">
        <div className="inner">
          {children}
          <SiteFooter />
        </div>
      </main>
    </div>
  );
}
