import type { Metadata, Viewport } from "next";
import Link from "next/link";
import { BookOpen, Search } from "lucide-react";
import "pretendard/dist/web/variable/pretendardvariable-dynamic-subset.css";
import "@fontsource-variable/jetbrains-mono";
import "./tokens.css";
import "./globals.css";
import SideNav from "@/components/SideNav";
import TopMenu from "@/components/TopMenu";
import ThemeToggle from "@/components/ThemeToggle";
import NavToggle from "@/components/NavToggle";
import SideToggle from "@/components/SideToggle";
import SearchDialog from "@/components/SearchDialog";
import Footer from "@/components/Footer";
import { NAME } from "@/lib/site";

export const metadata: Metadata = {
  title: { default: NAME, template: `%s · ${NAME}` },
  description: "AX 엔지니어가 되는 길(로드맵)과 그 길에 필요한 기초 강의, 업무 사례를 한곳에 모은 공개 자료예요.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: [{ color: "#FFFFFF" }],
};

// 처음에는 밝은 화면이에요. 오른쪽 위 버튼으로 고른 화면은 이 브라우저에 남겨 둬요.
const boot = `try{var t=localStorage.getItem('theme');document.documentElement.dataset.theme=t==='dark'?'dark':'light'}catch(e){}try{if(localStorage.getItem('side-closed')==='1')document.documentElement.dataset.side='closed'}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko" data-theme="light" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: boot }} />
      </head>
      <body>
        <a className="skip-link" href="#main">
          본문으로 건너뛰기
        </a>
        <header className="top">
          <Link className="brand" href="/" aria-label={`${NAME} 홈`}>
            <span className="mk">
              <BookOpen aria-hidden="true" />
            </span>
            <b>{NAME}</b>
          </Link>
          <SideToggle />
          <button className="sf" type="button" data-search aria-label="찾기">
            <Search className="i" aria-hidden="true" />
            <span>주제, 챕터, 명령어, 사례 찾기</span>
            <kbd>/</kbd>
          </button>
          <nav className="tn" aria-label="메뉴">
            <TopMenu />
            <Link className="st" href="/start/">
              시작하기
            </Link>
            <ThemeToggle />
            <NavToggle />
          </nav>
        </header>
        <div className="shell">
          <SideNav />
          <div className="scrim" aria-hidden="true" />
          <div className="body">
            <main className="main" id="main">
              {children}
            </main>
            <Footer />
          </div>
        </div>
        <SearchDialog />
      </body>
    </html>
  );
}
