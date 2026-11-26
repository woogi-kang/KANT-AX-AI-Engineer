import type { Metadata } from "next";
import Link from "next/link";
import { ChevronRight, Download, ExternalLink } from "lucide-react";
import DeckLayout from "@/components/DeckLayout";
import ChapterBody from "@/components/ChapterBody";
import Level from "@/components/Level";
import { deckUrl, getChapter, load, pdfUrl, slidesOf } from "@/lib/content";
import { renderReadme } from "@/lib/markdown";
import { plainInline, renderInline } from "@/lib/inline";

type Params = { params: Promise<{ dir: string }> };

export function generateStaticParams() {
  return load().chapters.map((c) => ({ dir: c.dir }));
}
export const dynamicParams = false;

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const c = getChapter((await params).dir);
  return { title: `${c.no} ${c.title}`, description: plainInline(c.goal) };
}

export default async function ChapterPage({ params }: Params) {
  const c = getChapter((await params).dir);
  const { html } = await renderReadme(c.dir);
  const slides = slidesOf(`${c.dir}/${c.slides}`);
  const color = `var(--t-${c.trackKey})`;
  const top = (
    <>
      <nav className="crumb" aria-label="위치">
        <Link href="/">커리큘럼</Link>
        <ChevronRight className="i" />
        <Link href={`/#stage-${c.stageNo}`}>
          {c.stageNo}단계 {c.stageTitle}
        </Link>
        <ChevronRight className="i" />
        <span>{c.groupTitle}</span>
      </nav>
      <div className="ov-head">
        <div>
          <span className="no" style={{ color }}>
            {c.no}
            <span className={`chip ${c.trackKey}`}>{c.track}</span>
            <Level level={c.level} />
          </span>
          <h1>{c.title}</h1>
          <p dangerouslySetInnerHTML={{ __html: renderInline(c.goal) }} />
        </div>
        <div className="act">
          <a className="btn secondary sm" href={deckUrl(c.dir, c.slides)} target="_blank" rel="noopener">
            <ExternalLink className="i" />새 창으로 보기
          </a>
          <a className="btn secondary sm" href={pdfUrl(c.dir, c.slides)} target="_blank" rel="noopener">
            <Download className="i" />
            PDF 받기
          </a>
        </div>
      </div>
    </>
  );
  return (
    <DeckLayout
      head={{ no: c.no, title: c.title, color }}
      slides={slides.map((s) => ({ n: s.n, title: s.title }))}
      src={deckUrl(c.dir, c.slides)}
      deckTitle={c.title}
      top={top}
    >
      <ChapterBody html={html} slides={slides} prev={c.prev} next={c.next} />
    </DeckLayout>
  );
}
