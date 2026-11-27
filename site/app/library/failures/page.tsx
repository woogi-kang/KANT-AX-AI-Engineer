import type { Metadata } from "next";
import Link from "next/link";
import { ghBlob } from "@/lib/roadmap";
import { renderRoadmapMd } from "@/lib/markdown";
import { library, homeOf, regionKo } from "@/lib/library";
import { Crumb, Ic, Ict, More, PageHead, SecHead } from "@/components/ui";
import LibTiles from "@/components/LibTiles";
import LibFilter from "@/components/LibFilter";
import OrgMark from "@/components/OrgMark";
import "../library.css";

export const metadata: Metadata = { title: "실패·중단 사례" };

export default async function FailuresPage() {
  const lib = library();
  const F = lib.fails;
  const src = "research/ax-failure-cases.md";
  const outs = [...new Set(F.flatMap((f) => f.outcome))].map((o) => ({ o, n: F.filter((f) => f.outcome.includes(o)).length })).sort((a, b) => b.n - a.n);
  const kr = F.filter((f) => f.region === "KR").length;
  const max = Math.max(...lib.causes.map((c) => c.n));
  const causeKo = (c: string) => lib.causes.find((x) => x.code === c)?.ko ?? c;
  const patternsHtml = await renderRoadmapMd(src, lib.failMeta.patterns);

  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["실패·중단 사례"]]} />
      <PageHead icon={<Ict n="triangle-exclamation-point" size="lg" />} title="실패·중단 사례" lede="AI를 도입했다가 멈추거나 되돌린 공개 기록이에요. 카드를 누르면 무슨 일이 있었고 무엇을 점검할지 볼 수 있어요." />
      <LibTiles on="failures" />

      <section className="sec">
        <SecHead title="반복되는 실패 원인" />
        <div className="lb-top">
          {lib.causes.slice(0, 4).map((c) => (
            <a key={c.code} className="tile" href={`?cause=${c.code}#fail-list`}>
              <span className="lb-top-n">
                {c.n}
                <small>건</small>
              </span>
              <b>{c.ko}</b>
              <small>{c.mean}</small>
            </a>
          ))}
        </div>
        <More label={`나머지 원인 ${lib.causes.length - 4}가지`}>
          <div className="lb-bars lb-causes">
            {lib.causes.slice(4).map((c) => (
              <a key={c.code} className="lb-bar" href={`?cause=${c.code}#fail-list`} title={c.mean}>
                <span className="lb-bl">{c.ko}</span>
                <span className="lb-track">
                  <i style={{ width: `${(c.n / max) * 100}%` }} />
                </span>
                <b>{c.n}</b>
              </a>
            ))}
          </div>
        </More>
        <p className="lb-note">한 사례에 원인을 여럿 붙였어요. 누르면 그 원인의 사례만 보여요.</p>
        <More label="세 가지 흐름이 반복돼요">
          <div className="prose" dangerouslySetInnerHTML={{ __html: patternsHtml }} />
        </More>
      </section>

      <section className="sec">
        <SecHead title={`사례 ${F.length}건`} right={<span className="cnt">확인 {lib.failMeta.checked}</span>} />
        <LibFilter
          target="#fail-list"
          search="조직, 업무 찾기"
          unit="건"
          groups={[
            { key: "out", label: "결과", options: outs.map(({ o, n }) => ({ value: o, label: lib.outShort(o), count: n })) },
            { key: "home", label: "국내/해외", options: [{ value: "kr", label: "국내", count: kr }, { value: "abroad", label: "해외", count: F.length - kr }] },
            { key: "cause", label: "원인", kind: "select", options: lib.causes.map((c) => ({ value: c.code, label: c.ko, count: c.n })) },
          ]}
        />
        <div className="lb-orgs" id="fail-list">
          {F.map((f) => (
            <Link key={f.id} id={f.id} href={`/library/failures/${f.id}/`} className="lb-org-card" data-item="" data-out={f.outcome.join(" ")} data-home={homeOf(f.region)} data-cause={f.causes.join(" ")} data-q={`${f.id} ${f.org} ${f.domain} ${f.change}`}>
              <OrgMark id={f.id} org={f.org} />
              <span className="lb-org-b">
                <b>{f.org}</b>
                <span className="lb-org-w">{f.domain}</span>
                <span className="lb-org-m">
                  {f.outcome.map((o) => (
                    <span key={o} className="badge err">
                      {lib.outShort(o)}
                    </span>
                  ))}
                  <span>{regionKo(f.region)}</span>
                </span>
                <span className="lb-org-c">
                  {f.causes.slice(0, 2).map((c) => causeKo(c)).join(" · ")}
                  {f.causes.length > 2 ? ` 외 ${f.causes.length - 2}` : ""}
                </span>
              </span>
              <Ic n="chevron-right" className="i lb-go" />
            </Link>
          ))}
        </div>
      </section>
      <section className="sec" id="캡스톤-설계에-쓰는-점검표">
        <span id="capstone" />
        <SecHead title="캡스톤 설계 점검표" right={<a href={ghBlob(`${src}#캡스톤-설계에-쓰는-점검표`)}>원문</a>} />
        <p className="lb-note" style={{ marginTop: 0 }}>
          캡스톤 업무를 고른 뒤 여덟 질문에 답해요. 답은{" "}
          <Link className="lk" href="/library/templates/execution-contract/">
            업무 실행 규칙
          </Link>
          과{" "}
          <Link className="lk" href="/library/templates/experiment-card/">
            실험 카드
          </Link>
          에 옮겨요. 아래 번호는 근거가 된 사례예요.
        </p>
        <ol className="lb-qs">
          {lib.capstone.map((c, n) => (
            <li key={n}>
              <span className="lb-qn">{n + 1}</span>
              <div>
                <p>{c.q}</p>
                <span className="chips">
                  {c.ids.map((id) => (
                    <a key={id} className="chip lb-id" href={`/library/failures/${id}/`}>
                      {id}
                    </a>
                  ))}
                </span>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <p className="lb-note">
        이 레포가 조직을 조사하거나 원인을 독립적으로 판정하지 않았어요. 원인은 읽은 출처가 설명한 범위에서 붙였어요. 원본: <a className="lk" href={ghBlob(src)}>research/ax-failure-cases.md</a>
      </p>
    </>
  );
}
