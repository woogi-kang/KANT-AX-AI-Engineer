import type { Metadata } from "next";
import { Download, Presentation } from "lucide-react";
import { deckUrl, getChapter, load, pdfUrl } from "@/lib/content";
import { chapterInfo } from "@/lib/chapter";
import { plainInline, renderInline } from "@/lib/inline";
import { Cover, Crumb, extraCoverSrc, Ict, PageHead, partSrc, SecHead } from "@/components/ui";
import Player from "@/components/Player";
import PartGo from "@/components/PartGo";
import LecCard from "@/components/LecCard";
import Lesson, { lessonSections } from "@/components/Lesson";
import "../../chapters/[dir]/chapter.css";

type Params = { params: Promise<{ dir: string }> };
const get = (dir: string) => {
  const e = load().extras.find((x) => x.dir === dir);
  if (!e) throw new Error(`없는 꿀팁 ${dir}`);
  return e;
};
export const dynamicParams = false;
export function generateStaticParams() {
  return load().extras.map((e) => ({ dir: e.dir }));
}
export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const e = get((await params).dir);
  return { title: `꿀팁 ${e.title}`, description: plainInline(e.summary) };
}

// 꿀팁 화면: 챕터 화면과 같은 모양(표지 플레이어, 파트 카드, 관련 챕터, 교안)
export default async function ExtraPage({ params }: Params) {
  const e = get((await params).dir);
  const rel = `extras/${e.dir}`;
  const { parts } = chapterInfo(rel);
  const secs = await lessonSections(rel, /^(학습 목표|구성|강사용)/);
  const deck = deckUrl(e.dir, e.slides, true);
  return (
    <>
      <Crumb items={[["강의", "/lectures/"], ["꿀팁", "/tips/"], [e.title]]} />
      <PageHead icon={<Ict n="lightbulb" size="lg" />} eyebrow="꿀팁" title={e.title} lede={<span dangerouslySetInnerHTML={{ __html: renderInline(e.summary) }} />} />
      <Player src={deck} cover={extraCoverSrc(e.dir)} title={e.title} />
      <div className="acts">
        <a href={deck} target="_blank" rel="noopener">
          <Presentation aria-hidden="true" />
          크게 보기
        </a>
        <a href={pdfUrl(e.dir, e.slides, true)} target="_blank" rel="noopener">
          <Download aria-hidden="true" />
          PDF 받기
        </a>
      </div>

      {parts.length > 0 && (
        <section className="sec">
          <SecHead title="구성" right={<span className="cnt">파트 {parts.length}개</span>} />
          <div className="tiles t4 parts-grid">
            {parts.map((p) => (
              <PartGo key={p.from} page={p.from} className="part" label={`${p.name}, ${p.from}쪽부터 슬라이드 보기`}>
                <Cover src={partSrc(rel, p.from)} />
                <span className="pt">
                  <b>{p.name}</b>
                  <small>
                    {p.from}
                    {p.to > p.from ? `–${p.to}` : ""}
                  </small>
                </span>
              </PartGo>
            ))}
          </div>
        </section>
      )}

      {e.relatedChapters.length > 0 && (
        <section className="sec">
          <SecHead title="관련 챕터" />
          <div className="tiles t4">
            {e.relatedChapters.map((r) => {
              const c = getChapter(r.dir);
              return <LecCard key={c.dir} c={c} sub={`${c.track} · ${c.level}`} />;
            })}
          </div>
        </section>
      )}

      <Lesson secs={secs} />
    </>
  );
}
