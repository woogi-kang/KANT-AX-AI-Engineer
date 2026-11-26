"use client";
import Link from "next/link";
import { useState } from "react";
import { ArrowRight } from "lucide-react";
import type { NewsItem } from "@/lib/content";
import { plainInline } from "@/lib/inline";

const short = (d: string) => `${d.slice(5, 7)}.${d.slice(8, 10)}`;

/** 새 소식 전체 목록. 릴리스 노트와 새 챕터로 거르고 달마다 묶어요. */
export default function NewsList({ items }: { items: NewsItem[] }) {
  const [f, setF] = useState<"all" | NewsItem["kind"]>("all");
  const shown = items.filter((i) => f === "all" || i.kind === f);
  const months: [string, NewsItem[]][] = [];
  for (const it of shown) {
    const m = `${it.date.slice(0, 4)}년 ${parseInt(it.date.slice(5, 7))}월`;
    const last = months[months.length - 1];
    if (last && last[0] === m) last[1].push(it);
    else months.push([m, [it]]);
  }
  const btn = (k: typeof f, label: string, n: number) => (
    <button type="button" aria-pressed={f === k} onClick={() => setF(k)}>
      {label} {n}
    </button>
  );
  return (
    <>
      <div className="filter" role="group" aria-label="종류" style={{ marginTop: 22 }}>
        {btn("all", "전체", items.length)}
        {btn("update", "업데이트 노트", items.filter((i) => i.kind === "update").length)}
        {btn("chapter", "새 챕터", items.filter((i) => i.kind === "chapter").length)}
      </div>
      <div className="news-list">
        {months.map(([m, list]) => (
          <section key={m}>
            <h2 className="news-month">{m}</h2>
            {list.map((it) => (
              <div className="news-row" key={it.href}>
                <time dateTime={it.date}>{short(it.date)}</time>
                <div>
                  <span className={`badge ${it.kind === "chapter" ? "run" : "mark"}`}>{it.tag}</span>
                  <b>{it.title}</b>
                  <p>{plainInline(it.summary)}</p>
                </div>
                <Link href={it.href}>
                  {it.kind === "chapter" ? "챕터 보기" : "자세히"} <ArrowRight className="i" />
                </Link>
              </div>
            ))}
          </section>
        ))}
      </div>
    </>
  );
}
