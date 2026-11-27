import type { Metadata } from "next";
import Link from "next/link";
import { ChevronLeft, ChevronRight, ExternalLink } from "lucide-react";
import { roadmap, ghBlob } from "@/lib/roadmap";
import { library, regionKo } from "@/lib/library";
import { caseIcon } from "@/lib/site";
import { Crumb, Ic, SecHead } from "@/components/ui";
import OrgMark from "@/components/OrgMark";
import "../../library.css";

type Params = { params: Promise<{ id: string }> };
export const dynamicParams = false;
export function generateStaticParams() {
  return library().fails.map((f) => ({ id: f.id }));
}
export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { id } = await params;
  const f = library().fails.find((x) => x.id === id);
  return { title: `${f?.org ?? ""} · 실패·중단 사례` };
}
const host = (u: string) => {
  try {
    return new URL(u).hostname.replace(/^www\./, "");
  } catch {
    return u;
  }
};

export default async function FailurePage({ params }: Params) {
  const { id } = await params;
  const lib = library();
  const r = roadmap();
  const k = lib.fails.findIndex((x) => x.id === id);
  const f = lib.fails[k];
  const prev = lib.fails[k - 1];
  const next = lib.fails[k + 1];
  const causes = f.causes.map((c) => lib.causes.find((x) => x.code === c)!).filter(Boolean);
  const qs = lib.capstone.map((c, n) => ({ ...c, n: n + 1 })).filter((c) => c.ids.includes(f.id));
  const related = f.related.map((cid) => r.cases.find((x) => x.id === cid)).filter((x) => !!x);

  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["실패·중단 사례", "/library/failures/"], [f.org]]} />
      <header className="lb-hero">
        <OrgMark id={f.id} org={f.org} size="lg" />
        <div>
          <p className="lb-hero-e">
            <span className="mono">{f.id}</span> · {regionKo(f.region)} · {f.domain}
          </p>
          <h1>{f.org}</h1>
          <p className="lb-hero-b">
            {f.outcome.map((o) => (
              <span key={o} className="badge lg err" title={lib.outMean(o)}>
                {lib.outShort(o)}
              </span>
            ))}
            {f.disclosed && <span className="muted lb-num">공개 {f.disclosed}</span>}
          </p>
        </div>
      </header>

      <div className="lb-story">
        <div className="tile">
          <small>
            <Ic n="target" />
            바꾸려 한 것
          </small>
          <p>{f.change}</p>
        </div>
        <div className="tile err">
          <small>
            <Ic n="circle-exclamation-point" />
            무슨 일이 있었나
          </small>
          <p>{f.happened}</p>
        </div>
      </div>

      <section className="lb-check lb-check-lg">
        <small>
          <Ic n="list-checks" />내 설계에서 점검할 것
        </small>
        <p>{f.check}</p>
      </section>

      <section className="sec">
        <SecHead title="왜 멈췄나" />
        <div className="lb-why">
          {causes.map((c) => (
            <Link key={c.code} href={`/library/failures/?cause=${c.code}#fail-list`} className="tile">
              <b>{c.ko}</b>
              <small>{c.mean}</small>
              <span className="muted">같은 원인 {c.n}건</span>
            </Link>
          ))}
        </div>
        <h3 className="lb-h3">판단 지표</h3>
        <p className="lb-p">{f.metric}</p>
      </section>

      {qs.length > 0 && (
        <section className="sec">
          <SecHead title="이 사례가 근거인 캡스톤 질문" right={<Link href="/library/failures/#캡스톤-설계에-쓰는-점검표">점검표 전체</Link>} />
          <ol className="lb-qs lb-qs-1">
            {qs.map((c) => (
              <li key={c.n}>
                <span className="lb-qn">{c.n}</span>
                <div>
                  <p>{c.q}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>
      )}

      <section className="sec">
        <SecHead title="근거" right={<span className="badge">{lib.evidShort(f.evidence)}</span>} />
        <p className="lb-p muted">{lib.evidMean(f.evidence)}</p>
        <div className="lb-links lb-links-1">
          {f.sources.map((s) => (
            <a key={s.url} href={s.url} target="_blank" rel="noopener">
              <ExternalLink aria-hidden="true" />
              <span>
                <b>{s.publisher || host(s.url)}</b>
                <small>{s.supports}</small>
                <small className="lb-num">
                  {s.published ? `발행 ${s.published} · ` : ""}확인 {s.checked}
                </small>
              </span>
            </a>
          ))}
        </div>
        {f.limits.length > 0 && (
          <div className="lb-limit">
            <b>한계</b>
            {f.limits.map((l) => (
              <p key={l}>{l}</p>
            ))}
          </div>
        )}
      </section>

      {related.length > 0 && (
        <section className="sec">
          <SecHead title="비슷한 업무를 직접 설계해 봐요" />
          <div className="lb-rels">
            {related.map((c) => (
              <Link key={c.id} className="tile lb-relc" href={`/library/cases/${c.id}/`}>
                <Ic n={caseIcon(c.area)} />
                <span>
                  <small>업무 사례 · {c.area}</small>
                  <b>{c.t}</b>
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}

      <p className="lb-note">
        이 레포가 조직을 조사하거나 원인을 독립적으로 판정하지 않았어요. 원인은 읽은 출처가 설명한 범위에서 붙였어요. 원본: <a className="lk" href={ghBlob("research/ax-failure-cases.md")}>research/ax-failure-cases.md</a>
      </p>

      <nav className="pn" aria-label="이전, 다음 실패 사례">
        {prev ? (
          <Link href={`/library/failures/${prev.id}/`}>
            <ChevronLeft className="i" aria-hidden="true" />
            <span>
              <small>이전 사례</small>
              <b>{prev.org}</b>
            </span>
          </Link>
        ) : (
          <span className="empty" />
        )}
        {next ? (
          <Link className="r" href={`/library/failures/${next.id}/`}>
            <ChevronRight className="i" aria-hidden="true" />
            <span>
              <small>다음 사례</small>
              <b>{next.org}</b>
            </span>
          </Link>
        ) : (
          <span className="empty" />
        )}
      </nav>
    </>
  );
}
