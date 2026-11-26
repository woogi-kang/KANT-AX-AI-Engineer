import type { Metadata } from "next";
import AppShell from "@/components/AppShell";
import NewsList from "@/components/NewsList";
import { news } from "@/lib/content";

export const metadata: Metadata = { title: "업데이트" };

export default function UpdatesPage() {
  return (
    <AppShell current="news">
      <h1 className="page-title">업데이트</h1>
      <p className="lede">슬라이드 보는 방법이 바뀌거나 새 챕터가 올라오면 여기에 남겨요.</p>
      <NewsList items={news()} />
    </AppShell>
  );
}
