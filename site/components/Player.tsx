"use client";
import { useEffect, useState } from "react";
import { Play } from "lucide-react";

/**
 * 슬라이드 자리. 처음에는 표지 그림만 보여 주고, 누르면 덱 플레이어(iframe)를 불러요.
 * 다른 곳에서 window.dispatchEvent(new CustomEvent("deck-go", { detail: 쪽 })) 하면 그 쪽으로 열어요.
 */
export default function Player({ src, cover, title }: { src: string; cover: string; title: string }) {
  const [page, setPage] = useState<number | null>(null);
  useEffect(() => {
    const go = (e: Event) => {
      setPage((e as CustomEvent<number>).detail || 1);
      document.getElementById("player")?.scrollIntoView({ behavior: "smooth", block: "center" });
    };
    addEventListener("deck-go", go);
    return () => removeEventListener("deck-go", go);
  }, []);
  return (
    <div className="player" id="player">
      {page === null ? (
        <button type="button" className="cover-btn" onClick={() => setPage(1)} aria-label={`${title} 슬라이드 보기`}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={cover} alt="" width={960} height={540} />
          <span className="play">
            <Play aria-hidden="true" />
            슬라이드 보기
          </span>
        </button>
      ) : (
        <iframe key={page} src={`${src}${page > 1 ? `#${page}` : ""}`} title={`${title} 슬라이드`} allow="fullscreen" />
      )}
    </div>
  );
}
