import type { Metadata } from "next";
import Link from "next/link";
import { load } from "@/lib/content";
import { Crumb, Cover, extraCoverSrc, Ict, PageHead } from "@/components/ui";

export const metadata: Metadata = { title: "꿀팁" };

export default function TipsPage() {
  const { extras } = load();
  return (
    <>
      <Crumb items={[["강의", "/lectures/"], ["꿀팁"]]} />
      <PageHead icon={<Ict n="lightbulb" size="lg" />} title="꿀팁" lede="배우는 순서와 상관없이 막혔을 때 펴 보는 자료예요." />
      <div className="tiles t3" style={{ marginTop: 24 }}>
        {extras.map((e) => (
          <Link key={e.dir} className="lc" href={`/extras/${e.dir}/`}>
            <Cover src={extraCoverSrc(e.dir)} />
            <div className="bd">
              <b>{e.title}</b>
              <small>관련 챕터 {e.relatedChapters.map((c) => c.no).join(", ")}</small>
            </div>
          </Link>
        ))}
      </div>
    </>
  );
}
