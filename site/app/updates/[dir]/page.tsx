import type { Metadata } from "next";
import Link from "next/link";
import { ChevronRight } from "lucide-react";
import AppShell from "@/components/AppShell";
import { load } from "@/lib/content";
import { renderReadme } from "@/lib/markdown";

type Params = { params: Promise<{ dir: string }> };
const get = (dir: string) => {
  const u = load().updates.find((x) => x.dir === dir);
  if (!u) throw new Error(`없는 릴리스 노트 ${dir}`);
  return u;
};

export function generateStaticParams() {
  return load().updates.map((u) => ({ dir: u.dir }));
}
export const dynamicParams = false;

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const u = get((await params).dir);
  return { title: u.title, description: u.summary };
}

export default async function UpdatePage({ params }: Params) {
  const u = get((await params).dir);
  const { html } = await renderReadme(`updates/${u.dir}`);
  return (
    <AppShell current="news">
      <nav className="crumb" aria-label="위치">
        <Link href="/updates/">소식</Link>
        <ChevronRight className="i" />
        <span>릴리스 노트</span>
      </nav>
      <div className="ov-head" style={{ paddingBottom: 0 }}>
        <div>
          <span className="no" style={{ color: "var(--muted)" }}>
            <time dateTime={u.date}>{u.date}</time>
          </span>
          <h1>{u.title}</h1>
        </div>
      </div>
      <article className="prose" style={{ marginTop: 16 }} dangerouslySetInnerHTML={{ __html: html }} />
    </AppShell>
  );
}
