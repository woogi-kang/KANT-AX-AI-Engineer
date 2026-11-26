import type { Metadata } from "next";
import { load } from "@/lib/content";
import { roadmap, topicBySlug, readRm, ghBlob } from "@/lib/roadmap";
import { topicChapters } from "@/lib/links";
import { renderRoadmapMd } from "@/lib/markdown";
import { AREA_IC, stageShort } from "@/lib/site";
import { Crumb, Ict, NumBox, PageHead, SecHead } from "@/components/ui";
import LecCard from "@/components/LecCard";

type Params = { params: Promise<{ slug: string }> };
export const dynamicParams = false;
export function generateStaticParams() {
  return roadmap().topics.map((t) => ({ slug: t.slug }));
}
export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const t = topicBySlug((await params).slug);
  return { title: `${t.t} · 로드맵`, description: t.q };
}

// 첫 판: 머리, 먼저 볼 강의, 로드맵 문서 전체. 로드맵 영역에서 v16 모양(알아야 할 것, 접는 절, 다음 주제)으로 다듬어요.
export default async function TopicPage({ params }: Params) {
  const t = topicBySlug((await params).slug);
  const r = roadmap();
  const stage = r.stages[t.stage - 1];
  const byNo = new Map(load().chapters.map((c) => [c.no, c]));
  const md = readRm(t.path).replace(/^# .+\n+/m, "");
  const html = await renderRoadmapMd(t.path, md);
  const nos = topicChapters(t.slug);
  return (
    <>
      <Crumb items={[["로드맵", "/roadmap/"], [`${t.stage}. ${stageShort(stage.title)}`, `/roadmap/#stage-${t.stage}`], [t.t]]} />
      <PageHead icon={AREA_IC[t.slug] ? <Ict n={AREA_IC[t.slug]} size="lg" /> : <NumBox>{`${t.stage}.${t.n}`}</NumBox>} title={t.t} lede={t.q} />
      {nos.length > 0 && (
        <section className="sec">
          <SecHead title="먼저 익힐 기초 강의" right={<span className="cnt">{nos.length}챕터</span>} />
          <div className="tiles t4">
            {nos.map((n) => (
              <LecCard key={n} c={byNo.get(n)!} />
            ))}
          </div>
        </section>
      )}
      <section className="sec">
        <SecHead title="로드맵 문서" right={<a href={ghBlob(t.path)}>원문</a>} />
        <article className="prose" dangerouslySetInnerHTML={{ __html: html }} />
      </section>
    </>
  );
}
