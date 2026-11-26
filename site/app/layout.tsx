import type { Metadata, Viewport } from "next";
import "pretendard/dist/web/variable/pretendardvariable-dynamic-subset.css";
import "@fontsource-variable/jetbrains-mono";
import "./tokens.css";
import "./globals.css";
import Header from "@/components/Header";

export const metadata: Metadata = {
  title: { default: "풀스택 AI/AX 엔지니어", template: "%s · 풀스택 AI/AX 엔지니어" },
  description: "터미널, Git, 파이썬, Docker, SQL, 데이터 분석을 배우는 순서대로 모은 무료 학습 사이트예요.",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#FFFFFF" },
    { media: "(prefers-color-scheme: dark)", color: "#1F242C" },
  ],
};

// 처음에는 밝은 화면이에요. 설정에서 고른 화면과 접은 메뉴는 브라우저에 남겨 둬요.
const boot = `try{var d=document.documentElement,t=localStorage.getItem('theme');d.dataset.theme=(t==='dark'||t==='light')?t:(t==='system'?'':'light');if(!d.dataset.theme)delete d.dataset.theme;if(localStorage.getItem('nav')==='closed')d.dataset.nav='closed'}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko" data-theme="light" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: boot }} />
      </head>
      <body>
        <a className="skip-link" href="#main">본문으로 건너뛰기</a>
        <Header />
        {children}
      </body>
    </html>
  );
}
