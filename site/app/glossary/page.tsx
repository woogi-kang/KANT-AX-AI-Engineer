import type { Metadata } from "next";
import { glossary } from "@/lib/search";
import { ghBlob } from "@/lib/roadmap";
import { renderMarkdown } from "@/lib/markdown";
import { Crumb, Ict, PageHead } from "@/components/ui";

export const metadata: Metadata = { title: "용어 사전" };

// 첫 판: 로드맵 레포의 비개발자 용어 안내. 로드맵 영역에서 v16 모양(가나다 거르기, 강의 연결)으로 다듬어요.
export default async function GlossaryPage() {
  const g = glossary();
  const md = async (s: string) => (await renderMarkdown(s)).replace(/^<p>|<\/p>\n?$/g, "");
  const rows = await Promise.all(g.map(async (x) => ({ ...x, term: await md(x.term), mean: await md(x.mean), ask: await md(x.ask) })));
  return (
    <>
      <Crumb items={[["홈", "/"], ["용어 사전"]]} />
      <PageHead icon={<Ict n="book-a" size="lg" />} title="용어 사전" lede="기술 용어를 외우기보다 어떤 결정과 위험을 가리키는지 봐요." />
      <div className="tiles t2" style={{ marginTop: 24 }}>
        {rows.map((x) => (
          <section key={x.id} id={x.id} className="tile">
            <b dangerouslySetInnerHTML={{ __html: x.term }} />
            <span style={{ fontSize: 15 }} dangerouslySetInnerHTML={{ __html: x.mean }} />
            <small dangerouslySetInnerHTML={{ __html: "물어볼 것: " + x.ask }} />
          </section>
        ))}
      </div>
      <p className="muted" style={{ fontSize: 13, marginTop: 12 }}>
        원본: <a href={ghBlob("start-here/non-developer-glossary.md")}>start-here/non-developer-glossary.md</a>
      </p>
    </>
  );
}
