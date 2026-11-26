import type { Metadata } from "next";
import Link from "next/link";
import { news } from "@/lib/content";
import { Crumb, Ict, PageHead } from "@/components/ui";
import FilterChips from "@/components/FilterChips";

export const metadata: Metadata = { title: "소식" };

export default function UpdatesPage() {
  const items = news();
  return (
    <>
      <Crumb items={[["홈", "/"], ["소식"]]} />
      <PageHead icon={<Ict n="megaphone" size="lg" />} title="소식" lede="슬라이드 보는 방법이 바뀌거나 새 챕터가 올라오면 여기에 남겨요." />
      <FilterChips
        target="#news-list"
        label="소식 종류"
        param="kind"
        options={[
          { value: "update", label: "업데이트", count: items.filter((n) => n.kind === "update").length },
          { value: "chapter", label: "새 챕터", count: items.filter((n) => n.kind === "chapter").length },
        ]}
      />
      <ul className="news" id="news-list">
        {items.map((n) => (
          <li key={n.href} data-f={n.kind}>
            <Link href={n.href}>
              <time dateTime={n.date}>{n.date}</time>
              <span className={n.kind === "update" ? "badge" : "badge ac"}>{n.kind === "update" ? "업데이트" : "새 챕터"}</span>
              <span>{n.title}</span>
            </Link>
          </li>
        ))}
      </ul>
    </>
  );
}
