import Link from "next/link";
import type { NewsItem } from "@/lib/content";
import { plainInline } from "@/lib/inline";

export const shortDate = (d: string) => `${d.slice(5, 7)}.${d.slice(8, 10)}`;

export default function NewsCard({ item }: { item: NewsItem }) {
  return (
    <Link className="news-card" href={item.href}>
      <span className="top">
        <span className={`badge ${item.kind === "chapter" ? "run" : "mark"}`}>{item.tag}</span>
        <time dateTime={item.date}>{shortDate(item.date)}</time>
      </span>
      <b>{item.title}</b>
      <p>{plainInline(item.summary)}</p>
    </Link>
  );
}
