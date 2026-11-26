import type { Metadata } from "next";
import { roadmap, readRm, ghBlob } from "@/lib/roadmap";
import { renderRoadmapMd } from "@/lib/markdown";
import { Crumb, Ict, PageHead, SecHead } from "@/components/ui";

type Params = { params: Promise<{ slug: string }> };
export const dynamicParams = false;
const get = (slug: string) => {
  const t = roadmap().templates.find((x) => x.slug === slug);
  if (!t) throw new Error(`없는 템플릿 ${slug}`);
  return t;
};
export function generateStaticParams() {
  return roadmap().templates.map((t) => ({ slug: t.slug }));
}
export async function generateMetadata({ params }: Params): Promise<Metadata> {
  return { title: `${get((await params).slug).t} · 실무 템플릿` };
}

// 첫 판: 템플릿 문서 전체. 사례와 자료 영역에서 복사 버튼과 v16 모양으로 다듬어요.
export default async function TemplatePage({ params }: Params) {
  const t = get((await params).slug);
  const html = await renderRoadmapMd(t.path, readRm(t.path).replace(/^# .+\n+/m, ""));
  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["실무 템플릿", "/library/templates/"], [t.t]]} />
      <PageHead icon={<Ict n="file-text" size="lg" />} title={t.t} lede={t.when} />
      <section className="sec">
        <SecHead title="양식" right={<a href={ghBlob(t.path)}>원문</a>} />
        <article className="prose" dangerouslySetInnerHTML={{ __html: html }} />
      </section>
    </>
  );
}
