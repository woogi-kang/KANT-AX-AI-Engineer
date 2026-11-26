import type { Metadata } from "next";
import { roadmap, ghBlob } from "@/lib/roadmap";
import { Crumb, Ict, PageHead } from "@/components/ui";
import LibTiles from "@/components/LibTiles";

export const metadata: Metadata = { title: "채용 현황" };

// 첫 판: 숫자 타일. 사례와 자료 영역에서 달별 그림과 공고 목록으로 다듬어요.
export default function JobsPage() {
  const r = roadmap();
  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["채용 현황"]]} />
      <PageHead icon={<Ict n="chart-column" size="lg" />} title="채용 현황" lede={r.hiring.lede} />
      <LibTiles on="jobs" />
      <div className="tiles t3" style={{ marginTop: 24 }}>
        {r.hiring.rows.map((h) => (
          <div key={h.type} className="tile">
            <span className="num">{h.n}</span>
            <b>{h.type}</b>
            <small>모집 중 {h.open}건</small>
          </div>
        ))}
      </div>
      <p className="muted" style={{ fontSize: 13, marginTop: 12 }}>
        {r.hiring.note} 원본: <a href={ghBlob("research/hiring-monthly/README.md")}>research/hiring-monthly</a>
      </p>
    </>
  );
}
