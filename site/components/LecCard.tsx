import Link from "next/link";
import type { Chapter } from "@/lib/content";
import { chapterLogos } from "@/lib/logos";
import { Cover, coverSrc, Logos } from "./ui";

/** 챕터 표지 카드 */
export default function LecCard({ c, logoSize = 24, sub }: { c: Chapter; logoSize?: number; sub?: React.ReactNode }) {
  return (
    <Link className="lc" href={`/chapters/${c.dir}/`}>
      <Cover src={coverSrc(c.no)} />
      <div className="bd">
        <Logos ks={chapterLogos(c.no, c.track)} size={logoSize} />
        <b>
          {c.no} {c.title}
        </b>
        {sub && <small>{sub}</small>}
      </div>
    </Link>
  );
}
