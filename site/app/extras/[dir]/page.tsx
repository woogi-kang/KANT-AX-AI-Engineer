import type { Metadata } from "next";
import Link from "next/link";
import { Download, Presentation, ChevronDown } from "lucide-react";
import { deckUrl, load, pdfUrl } from "@/lib/content";
import { renderReadme } from "@/lib/markdown";
import { splitSections } from "@/lib/chapter";
import { plainInline, renderInline } from "@/lib/inline";
import { shortTitle } from "@/lib/site";
import { Crumb, extraCoverSrc, Ict, PageHead, SecHead } from "@/components/ui";
import Player from "@/components/Player";

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

export default async function ExtraPage({ params }: Params) {
  const e = get((await params).dir);
  const { html } = await renderReadme(`extras/${e.dir}`);
  const secs = splitSections(html).filter((s) => !/^강사용/.test(s.title));
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
      <p className="muted" style={{ marginTop: 16, fontSize: 14 }}>
        관련 챕터:{" "}
        {e.relatedChapters.map((c, n) => (
          <span key={c.dir}>
            {n > 0 && ", "}
            <Link href={`/chapters/${c.dir}/`} style={{ color: "var(--ac)" }}>
              {c.no} {shortTitle(c.title)}
            </Link>
          </span>
        ))}
      </p>
      <section className="sec doc">
        <SecHead title="교안" />
        {secs.map((s) => (
          <details key={s.id} id={s.id}>
            <summary>
              {s.title}
              <ChevronDown aria-hidden="true" />
            </summary>
            <div className="in prose" dangerouslySetInnerHTML={{ __html: s.html }} />
          </details>
        ))}
      </section>
    </>
  );
}
