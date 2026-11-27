import type { Metadata } from "next";
import Link from "next/link";
import { ghBlob } from "@/lib/roadmap";
import { library, homeOf, regionKo, stageTone, IND_KO } from "@/lib/library";
import { Crumb, Ic, Ict, PageHead } from "@/components/ui";
import LibTiles from "@/components/LibTiles";
import LibFilter from "@/components/LibFilter";
import OrgMark from "@/components/OrgMark";
import "../library.css";

export const metadata: Metadata = { title: "공개 AX 사례" };

const count = <T,>(xs: T[], f: (x: T) => string) => {
  const m = new Map<string, number>();
  for (const x of xs) m.set(f(x), (m.get(f(x)) ?? 0) + 1);
  return [...m.entries()].sort((a, b) => b[1] - a[1]);
};
const STAGE_ORDER = ["operation", "limited-operation", "pilot", "adjusted-operation", "unknown"];
const VERIFY_ORDER = ["cross-checked", "self-reported", "none"];

export default function PublicPage() {
  const lib = library();
  const P = lib.pub;
  const src = "research/public-ax-cases.md";
  const kr = P.filter((p) => p.region === "KR").length;
  const stages = count(P, (p) => p.stage).sort((a, b) => STAGE_ORDER.indexOf(a[0]) - STAGE_ORDER.indexOf(b[0]));
  const verifies = count(P, (p) => p.verify).sort((a, b) => VERIFY_ORDER.indexOf(a[0]) - VERIFY_ORDER.indexOf(b[0]));
  const inds = count(P, (p) => p.ind);

  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["공개 AX 사례"]]} />
      <PageHead icon={<Ict n="file-check" size="lg" />} title="공개 AX 사례" lede="회사와 기관이 직접 공개한 AX 업무 사례예요. 카드를 누르면 흐름과 근거를 볼 수 있어요." />
      <LibTiles on="public" />

      <LibFilter
        target="#pub-list"
        search="회사, 업무 찾기"
        unit="건"
        groups={[
          { key: "home", label: "국내/해외", options: [{ value: "kr", label: "국내", count: kr }, { value: "abroad", label: "해외", count: P.length - kr }] },
          { key: "ind", label: "산업", kind: "select", options: inds.map(([i, n]) => ({ value: i, label: IND_KO[i] ?? i, count: n })) },
          { key: "stage", label: "도입 단계", kind: "select", options: stages.map(([s, n]) => ({ value: s, label: lib.stageKo(s), count: n })) },
          { key: "verify", label: "성과 검증", kind: "select", options: verifies.map(([v, n]) => ({ value: v, label: lib.verifyKo(v), count: n })) },
        ]}
      />

      <div className="lb-orgs" id="pub-list">
        {P.map((p) => (
          <Link key={p.id} id={p.id} href={`/library/public/${p.id}/`} className="lb-org-card" data-item="" data-home={homeOf(p.region)} data-stage={p.stage} data-verify={p.verify} data-ind={p.ind} data-q={`${p.id} ${p.org} ${p.w} ${IND_KO[p.ind] ?? ""}`}>
            <OrgMark id={p.id} org={p.org} />
            <span className="lb-org-b">
              <b>{p.org}</b>
              <span className="lb-org-w">{p.w}</span>
              <span className="lb-org-m">
                <span className={`badge ${stageTone(p.stage)}`}>{lib.stageKo(p.stage)}</span>
                <span>
                  {regionKo(p.region)} · {IND_KO[p.ind] ?? p.ind}
                </span>
              </span>
            </span>
            <Ic n="chevron-right" className="i lb-go" />
          </Link>
        ))}
      </div>
      <p className="lb-note">
        성과는 회사가 직접 밝힌 내용이고 독립 검증이 아니에요. 로고가 없는 곳은 이름 첫 글자로 보여 줘요. 상표는 각 회사의 것이에요(<a className="lk" href="/legal/">이용 안내</a>). 원본: <a className="lk" href={ghBlob(src)}>research/public-ax-cases.md</a>
      </p>
    </>
  );
}
