import type { Metadata } from "next";
import { roadmap, ghBlob } from "@/lib/roadmap";
import { Crumb, Ict, PageHead } from "@/components/ui";
import LibTiles from "@/components/LibTiles";

export const metadata: Metadata = { title: "실패·중단 사례" };

// 첫 판: 표 하나. 사례와 자료 영역에서 v16 카드와 결과별 거르기로 다듬어요.
export default function FailuresPage() {
  const r = roadmap();
  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["실패·중단 사례"]]} />
      <PageHead icon={<Ict n="triangle-exclamation-point" size="lg" />} title="실패·중단 사례" lede="바꾸려던 일, 결과, 원인, 다시 하지 않을 점검을 모았어요." />
      <LibTiles on="failures" />
      <div className="tw" style={{ marginTop: 24 }}>
        <table>
          <thead>
            <tr>
              <th>조직</th>
              <th>바꾸려던 일</th>
              <th>결과</th>
              <th>점검</th>
            </tr>
          </thead>
          <tbody>
            {r.failures.map((c) => (
              <tr key={c.id} id={c.id}>
                <td>{c.org}</td>
                <td>{c.change}</td>
                <td>{c.outcome}</td>
                <td>{c.check}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted" style={{ fontSize: 13 }}>
        원본: <a href={ghBlob("research/ax-failure-cases.md")}>research/ax-failure-cases.md</a>
      </p>
    </>
  );
}
