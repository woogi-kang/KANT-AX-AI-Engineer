"use client";
import { useEffect, useRef, useState } from "react";
import NavScrim from "./NavScrim";

type Slide = { n: number; title: string };
type Props = {
  head: { no: string; title: string; color: string };
  slides: Slide[];
  src: string;
  deckTitle: string;
  top: React.ReactNode;
  children: React.ReactNode;
};

/**
 * 챕터 화면 틀. 왼쪽에 장 목록, 가운데에 덱 플레이어(tools/build_player.js로 만든 HTML)를 그대로 넣어요.
 * 플레이어는 주소 끝 #쪽번호로 장을 옮기고, 장을 넘기면 주소를 #쪽번호로 바꿔요. 같은 사이트라 그 값을 읽어 목록에 표시해요.
 */
export default function DeckLayout({ head, slides, src, deckTitle, top, children }: Props) {
  const frame = useRef<HTMLIFrameElement>(null);
  const [cur, setCur] = useState(1);
  const listRef = useRef<HTMLOListElement>(null);

  useEffect(() => {
    const t = setInterval(() => {
      try {
        const h = frame.current?.contentWindow?.location.hash ?? "";
        const n = parseInt(h.slice(1)) || 1;
        setCur((c) => (c === n ? c : n));
      } catch {}
    }, 400);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const a = listRef.current?.querySelector<HTMLElement>(`[data-n="${cur}"]`);
    a?.scrollIntoView({ block: "nearest" });
  }, [cur]);

  const go = (n: number) => {
    const w = frame.current?.contentWindow;
    if (!w) return;
    w.location.hash = String(n);
    setCur(n);
    delete document.documentElement.dataset.drawer;
    frame.current?.focus();
  };

  return (
    <div className="chap">
      <aside className="sidebar" aria-label="장 목록">
        <div className="head">
          <span className="no" style={{ color: head.color }}>
            {head.no}
          </span>
          <b>{head.title}</b>
        </div>
        <ol className="slides" ref={listRef}>
          {slides.map((s) => (
            <li key={s.n}>
              <a
                href={`#slide-${s.n}`}
                data-n={s.n}
                aria-current={cur === s.n ? "true" : undefined}
                onClick={(e) => {
                  e.preventDefault();
                  go(s.n);
                }}
              >
                <span className="s">{s.n}</span>
                <span>{s.title}</span>
              </a>
            </li>
          ))}
        </ol>
      </aside>
      <NavScrim />
      <main className="chap-main" id="main">
        <div className="inner">
          {top}
          <div className="slide-box">
            <iframe ref={frame} src={src} title={`${deckTitle} 슬라이드`} allow="fullscreen; clipboard-write" allowFullScreen />
          </div>
          {children}
        </div>
      </main>
    </div>
  );
}
