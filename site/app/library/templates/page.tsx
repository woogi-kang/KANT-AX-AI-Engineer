import type { Metadata } from "next";
import Link from "next/link";
import { roadmap } from "@/lib/roadmap";
import { Crumb, Ict, PageHead } from "@/components/ui";
import LibTiles from "@/components/LibTiles";

export const metadata: Metadata = { title: "실무 템플릿" };

export default function TemplatesPage() {
  const r = roadmap();
  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["실무 템플릿"]]} />
      <PageHead icon={<Ict n="clipboard-check" size="lg" />} title="실무 템플릿" lede="업무를 바꿀 때 빠뜨리기 쉬운 판단과 책임을 확인하는 양식이에요." />
      <LibTiles on="templates" />
      <div className="tiles t4" style={{ marginTop: 24 }}>
        {r.templates.map((t) => (
          <Link key={t.slug} className="tile" href={`/library/templates/${t.slug}/`}>
            <Ict n="file-text" />
            <b>{t.t}</b>
            {t.when && <small>{t.when}</small>}
          </Link>
        ))}
      </div>
    </>
  );
}
