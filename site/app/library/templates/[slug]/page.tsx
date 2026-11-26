import type { Metadata } from "next";
import Link from "next/link";
import { ChevronLeft, ChevronRight, Download, ExternalLink } from "lucide-react";
import { roadmap, readRm, ghBlob, sections, strip } from "@/lib/roadmap";
import { renderRoadmapMd } from "@/lib/markdown";
import { Crumb, Ict, PageHead, SecHead } from "@/components/ui";
import CopyText from "@/components/CopyText";
import "../../library.css";

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

export default async function TemplatePage({ params }: Params) {
  const t = get((await params).slug);
  const all = roadmap().templates;
  const k = all.findIndex((x) => x.slug === t.slug);
  const prev = all[k - 1];
  const next = all[k + 1];
  const raw = readRm(t.path);
  const body = raw.replace(/^# .+\n+/m, "");
  const blocks = body.split("\n\n");
  const h2 = blocks.findIndex((b) => /^## /.test(b.trim()));
  const li = blocks.findIndex((b, n) => (h2 < 0 || n < h2) && b.trim() !== "" && !/^[#|>-]/.test(b.trim()));
  const lede = li >= 0 ? strip(blocks[li]) : "";
  const html = await renderRoadmapMd(t.path, blocks.filter((_, n) => n !== li).join("\n\n"));
  const heads = sections(raw).map((s) => s.title);
  const slugOf = (h: string) =>
    h
      .toLowerCase()
      .replace(/[^\p{L}\p{N}\s-]/gu, "")
      .trim()
      .replace(/\s/g, "-");
  const same = all.filter((x) => x.when === t.when && x.slug !== t.slug);
  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["실무 템플릿", "/library/templates/"], [t.t]]} />
      <PageHead icon={<Ict n="file-text" size="lg" />} title={t.t} />
      <div className="lb-whenbox">
        <small>언제 쓰나요</small>
        <b>{t.when}</b>
      </div>
      {lede && <p className="lede">{lede}</p>}
      <div className="acts">
        <CopyText text={raw} label="마크다운 복사" className="btn pri" />
        <a className="btn" href={`data:text/markdown;charset=utf-8,${encodeURIComponent(raw)}`} download={`${t.slug}.md`}>
          <Download aria-hidden="true" />
          .md 파일 받기
        </a>
        <a className="btn" href={ghBlob(t.path)} target="_blank" rel="noopener">
          원문
          <ExternalLink aria-hidden="true" />
        </a>
      </div>
      {same.length > 0 && (
        <p className="lb-note">
          같은 때 쓰는 양식:{" "}
          {same.map((s, n) => (
            <span key={s.slug}>
              {n > 0 && " · "}
              <Link className="lk" href={`/library/templates/${s.slug}/`}>
                {s.t}
              </Link>
            </span>
          ))}
        </p>
      )}
      <section className="sec">
        <SecHead title="양식" right={<span className="cnt">{heads.length}개 항목</span>} />
        <nav className="chips lb-toc" aria-label="양식 항목">
          {heads.map((h) => (
            <a key={h} className="chip lb-chip" href={`#${slugOf(h)}`}>
              {h}
            </a>
          ))}
        </nav>
        <article className="prose lb-tplbody" dangerouslySetInnerHTML={{ __html: html }} />
      </section>
      <nav className="pn" aria-label="이전, 다음 양식">
        {prev ? (
          <Link href={`/library/templates/${prev.slug}/`}>
            <ChevronLeft className="i" aria-hidden="true" />
            <span>
              <small>이전 양식</small>
              <b>{prev.t}</b>
            </span>
          </Link>
        ) : (
          <span className="empty" />
        )}
        {next ? (
          <Link className="r" href={`/library/templates/${next.slug}/`}>
            <ChevronRight className="i" aria-hidden="true" />
            <span>
              <small>다음 양식</small>
              <b>{next.t}</b>
            </span>
          </Link>
        ) : (
          <span className="empty" />
        )}
      </nav>
    </>
  );
}
