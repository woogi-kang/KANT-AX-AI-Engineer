import type { Metadata } from "next";
import Link from "next/link";
import { ChevronRight, Download, ExternalLink } from "lucide-react";
import DeckLayout from "@/components/DeckLayout";
import ChapterBody from "@/components/ChapterBody";
import { deckUrl, load, pdfUrl, slidesOf } from "@/lib/content";
import { renderReadme } from "@/lib/markdown";
import { plainInline, renderInline } from "@/lib/inline";

type Params = { params: Promise<{ dir: string }> };

const get = (dir: string) => {
  const e = load().extras.find((x) => x.dir === dir);
  if (!e) throw new Error(`없는 번외 ${dir}`);
  return e;
};

export function generateStaticParams() {
  return load().extras.map((e) => ({ dir: e.dir }));
}
export const dynamicParams = false;

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const e = get((await params).dir);
  return { title: `번외 ${e.title}`, description: plainInline(e.summary) };
}

export default async function ExtraPage({ params }: Params) {
  const e = get((await params).dir);
  const { html } = await renderReadme(`extras/${e.dir}`);
  const slides = slidesOf(`extras/${e.dir}/${e.slides}`);
  const top = (
    <>
      <nav className="crumb" aria-label="위치">
        <Link href="/">커리큘럼</Link>
        <ChevronRight className="i" />
        <Link href="/#extras">번외</Link>
      </nav>
      <div className="ov-head">
        <div>
          <span className="no" style={{ color: "var(--muted)" }}>
            번외
          </span>
          <h1>{e.title}</h1>
          <p dangerouslySetInnerHTML={{ __html: renderInline(e.summary) }} />
        </div>
        <div className="act">
          <a className="btn secondary sm" href={deckUrl(e.dir, e.slides, true)} target="_blank" rel="noopener">
            <ExternalLink className="i" />새 창으로 보기
          </a>
          <a className="btn secondary sm" href={pdfUrl(e.dir, e.slides, true)} target="_blank" rel="noopener">
            <Download className="i" />
            PDF 받기
          </a>
        </div>
      </div>
      <div className="related" style={{ margin: "0 0 16px" }}>
        관련 챕터
        {e.relatedChapters.map((r) => (
          <Link className="prereq" key={r.dir} href={`/chapters/${r.dir}/`}>
            <b>{r.no}</b>
            {r.title}
          </Link>
        ))}
      </div>
    </>
  );
  return (
    <DeckLayout head={{ no: "번외", title: e.title, color: "var(--muted)" }} slides={slides.map((s) => ({ n: s.n, title: s.title }))} src={deckUrl(e.dir, e.slides, true)} deckTitle={e.title} top={top}>
      <ChapterBody html={html} slides={slides} />
    </DeckLayout>
  );
}
