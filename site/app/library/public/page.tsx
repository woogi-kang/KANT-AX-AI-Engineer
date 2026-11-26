import type { Metadata } from "next";
import { roadmap, ghBlob } from "@/lib/roadmap";
import { Crumb, Ict, PageHead } from "@/components/ui";
import LibTiles from "@/components/LibTiles";

export const metadata: Metadata = { title: "공개 AX 사례" };

// 첫 판: 표 하나. 사례와 자료 영역에서 v16 카드, 산업·지역·근거 거르기로 다듬어요.
export default function PublicPage() {
  const r = roadmap();
  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["공개 AX 사례"]]} />
      <PageHead icon={<Ict n="file-check" size="lg" />} title="공개 AX 사례" lede="회사와 기관이 공개한 AX 사례예요. 주장마다 출처와 확인일이 있어요." />
      <LibTiles on="public" />
      <div className="tw" style={{ marginTop: 24 }}>
        <table>
          <thead>
            <tr>
              <th>번호</th>
              <th>조직</th>
              <th>바꾼 업무</th>
              <th>단계</th>
            </tr>
          </thead>
          <tbody>
            {r.publicCases.map((c) => (
              <tr key={c.id} id={c.id}>
                <td className="mono">{c.id}</td>
                <td>{c.org}</td>
                <td>{c.w}</td>
                <td>{c.stage}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted" style={{ fontSize: 13 }}>
        원본: <a href={ghBlob("research/public-ax-cases.md")}>research/public-ax-cases.md</a>
      </p>
    </>
  );
}
