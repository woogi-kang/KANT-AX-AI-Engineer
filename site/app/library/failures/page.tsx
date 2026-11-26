import type { Metadata } from "next";
import Link from "next/link";
import { ChevronDown, ExternalLink } from "lucide-react";
import { roadmap, ghBlob } from "@/lib/roadmap";
import { renderRoadmapMd } from "@/lib/markdown";
import { library, homeOf, regionKo } from "@/lib/library";
import { caseIcon } from "@/lib/site";
import { Crumb, Ic, Ict, More, PageHead, SecHead } from "@/components/ui";
import LibTiles from "@/components/LibTiles";
import LibFilter from "@/components/LibFilter";
import "../library.css";

export const metadata: Metadata = { title: "실패·중단 사례" };

const host = (u: string) => {
  try {
    return new URL(u).hostname.replace(/^www\./, "");
  } catch {
    return u;
  }
};

export default async function FailuresPage() {
  const lib = library();
  const r = roadmap();
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
      <PageHead icon={<Ict n="triangle-exclamation-point" size="lg" />} title="실패·중단 사례" lede="AI를 도입했다가 멈추거나 되돌린 공개 기록이에요. 무엇을 바꾸려 했고, 왜 멈췄고, 내 설계에서 무엇을 점검할지 모았어요." />
      <LibTiles on="failures" />

      <section className="sec" id="capstone">
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
                    <a key={id} className="chip lb-id" href={`#${id}`}>
                      {id}
                    </a>
                  ))}
                </span>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="sec">
        <SecHead title="반복되는 실패 원인" />
        <div className="lb-bars lb-causes">
          {lib.causes.map((c) => (
            <a key={c.code} className="lb-bar" href={`?cause=${c.code}#fail-list`} title={c.mean}>
              <span className="lb-bl">{c.ko}</span>
              <span className="lb-track">
                <i style={{ width: `${(c.n / max) * 100}%` }} />
              </span>
              <b>{c.n}</b>
            </a>
          ))}
        </div>
        <p className="lb-note">한 사례에 원인을 여럿 붙여서 합계는 16건보다 많아요. 막대를 누르면 그 원인의 사례만 보여요.</p>
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
        <div className="lb-cards" id="fail-list">
          {F.map((f) => (
            <article key={f.id} id={f.id} className="lb-card" data-item="" data-out={f.outcome.join(" ")} data-home={homeOf(f.region)} data-cause={f.causes.join(" ")} data-q={`${f.id} ${f.org} ${f.domain} ${f.change}`}>
              <div className="lb-card-h">
                <span className="mono muted">{f.id}</span>
                <span className="badge">{regionKo(f.region)}</span>
                {f.outcome.map((o) => (
                  <span key={o} className="badge err" title={lib.outMean(o)}>
                    {lib.outShort(o)}
                  </span>
                ))}
              </div>
              <b className="lb-org">{f.org}</b>
              <p className="lb-w">{f.domain}</p>
              <p className="lb-chg">{f.change}</p>
              <div className="chips">
                {f.causes.map((c) => (
                  <span key={c} className="chip lb-cause">
                    {causeKo(c)}
                  </span>
                ))}
              </div>
              <div className="lb-check">
                <small>
                  <Ic n="list-checks" />내 설계에서 점검할 것
                </small>
                <p>{f.check}</p>
              </div>
              <details className="lb-det">
                <summary>
                  무슨 일이 있었나, 판단 지표, 출처
                  <ChevronDown aria-hidden="true" />
                </summary>
                <div className="lb-detb">
                  <h4>무슨 일이 있었나</h4>
                  <p>{f.happened}</p>
                  <h4>판단 지표</h4>
                  <p>{f.metric}</p>
                  <h4>
                    근거 <span className="badge">{lib.evidShort(f.evidence)}</span>
                  </h4>
                  <p className="muted">{lib.evidMean(f.evidence)}</p>
                  <ul className="lb-src">
                    {f.sources.map((s) => (
                      <li key={s.url}>
                        <a className="lk" href={s.url} target="_blank" rel="noopener">
                          {s.publisher || host(s.url)}
                          <ExternalLink className="lb-ext" aria-hidden="true" />
                        </a>
                        <span className="muted lb-num">
                          {s.published ? ` 발행 ${s.published}` : ""} · 확인 {s.checked}
                        </span>
                        <small>{s.supports}</small>
                      </li>
                    ))}
                  </ul>
                  {f.limits.length > 0 && (
                    <>
                      <h4>한계</h4>
                      {f.limits.map((l) => (
                        <p key={l}>{l}</p>
                      ))}
                    </>
                  )}
                </div>
              </details>
              {f.related.length > 0 && (
                <div className="chips">
                  {f.related.map((id) => {
                    const cs = r.cases.find((x) => x.id === id);
                    return cs ? (
                      <Link key={id} className="chip lb-chip" href={`/library/cases/${id}/`}>
                        <Ic n={caseIcon(cs.area)} />
                        실습 사례: {cs.t}
                      </Link>
                    ) : null;
                  })}
                </div>
              )}
            </article>
          ))}
        </div>
      </section>
      <p className="lb-note">
        이 레포가 조직을 조사하거나 원인을 독립적으로 판정하지 않았어요. 원인은 읽은 출처가 설명한 범위에서 붙였어요. 원본: <a className="lk" href={ghBlob(src)}>research/ax-failure-cases.md</a>
      </p>
    </>
  );
}
