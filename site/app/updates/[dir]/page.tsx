import type { Metadata } from "next";
import { Crumb, Ict, PageHead } from "@/components/ui";
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
    <>
      <Crumb items={[["소식", "/updates/"], [u.title]]} />
      <PageHead icon={<Ict n="megaphone" size="lg" />} eyebrow={<time dateTime={u.date}>{u.date}</time>} title={u.title} lede={u.summary} />
      <article className="prose sec" style={{ marginTop: 32 }} dangerouslySetInnerHTML={{ __html: html }} />
    </>
  );
}
