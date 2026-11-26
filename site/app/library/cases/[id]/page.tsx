import type { Metadata } from "next";
import { roadmap, readRm, ghBlob } from "@/lib/roadmap";
import { renderRoadmapMd } from "@/lib/markdown";
import { caseIcon } from "@/lib/site";
import { Crumb, Diff, Ict, PageHead, SecHead } from "@/components/ui";

type Params = { params: Promise<{ id: string }> };
export const dynamicParams = false;
const get = (id: string) => {
  const c = roadmap().cases.find((x) => x.id === id);
  if (!c) throw new Error(`없는 업무 사례 ${id}`);
  return c;
};
export function generateStaticParams() {
  return roadmap().cases.map((c) => ({ id: c.id }));
}
export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const c = get((await params).id);
  return { title: `${c.t} · 업무 사례` };
}

// 첫 판: 사례 README 전체. 사례와 자료 영역에서 v16 모양(요약 타일, 접는 절, 실행 예제)으로 다듬어요.
export default async function CasePage({ params }: Params) {
  const c = get((await params).id);
  const md = readRm(c.path).replace(/^# .+\n+/m, "");
  const html = await renderRoadmapMd(c.path, md);
  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["업무 사례", "/library/"], [c.t]]} />
      <PageHead icon={<Ict n={caseIcon(c.area)} size="lg" />} eyebrow={`${c.area} · ${c.industry}`} title={c.t} />
      <p className="lede" style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <Diff v={c.diff} /> <span>위험 {c.risk}</span> <span>{c.p}</span>
      </p>
      <section className="sec">
        <SecHead title="사례 문서" right={<a href={ghBlob(c.path)}>원문</a>} />
        <article className="prose" dangerouslySetInnerHTML={{ __html: html }} />
      </section>
    </>
  );
}
