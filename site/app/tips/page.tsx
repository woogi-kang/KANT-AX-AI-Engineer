import type { Metadata } from "next";
import Link from "next/link";
import { load } from "@/lib/content";
import { plainInline } from "@/lib/inline";
import { Crumb, Cover, extraCoverSrc, Ict, PageHead } from "@/components/ui";
import { chapterLogos } from "@/lib/logos";
import { Logos } from "@/components/ui";
import "./tips.css";

export const metadata: Metadata = { title: "꿀팁", description: "배우는 순서와 상관없이 막혔을 때 펴 보는 자료예요." };

export default function TipsPage() {
  const { extras, chapters } = load();
  return (
    <>
      <Crumb items={[["강의", "/lectures/"], ["꿀팁"]]} />
      <PageHead icon={<Ict n="lightbulb" size="lg" />} title="꿀팁" lede={`배우는 순서와 상관없이 막혔을 때 펴 보는 자료예요. 지금 ${extras.length}개가 있어요.`} />
      <div className="tiles t3" style={{ marginTop: 24 }}>
        {extras.map((e) => {
          const rel = e.relatedChapters.map((r) => chapters.find((c) => c.dir === r.dir)!);
          const logos = [...new Set(rel.flatMap((c) => chapterLogos(c.no, c.track)))].slice(0, 4);
          return (
            <Link key={e.dir} className="lc" href={`/extras/${e.dir}/`}>
              <Cover src={extraCoverSrc(e.dir)} />
              <div className="bd">
                <Logos ks={logos} size={24} />
                <b>{e.title}</b>
                <small className="clamp2">{plainInline(e.summary)}</small>
                <small>관련 강의 {e.relatedChapters.map((c) => `${c.stageTitle} ${c.seq}`).join(", ")}</small>
              </div>
            </Link>
          );
        })}
      </div>
    </>
  );
}
