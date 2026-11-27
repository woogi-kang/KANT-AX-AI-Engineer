import type { Metadata } from "next";
import Link from "next/link";
import { ChevronLeft, ChevronRight, ExternalLink } from "lucide-react";
import { roadmap, ghBlob } from "@/lib/roadmap";
import { renderRoadmapMd } from "@/lib/markdown";
import { library, regionKo, stageTone, verifyTone, IND_KO } from "@/lib/library";
import { caseIcon } from "@/lib/site";
import { Crumb, Ic, More, SecHead } from "@/components/ui";
import OrgMark from "@/components/OrgMark";
import "../../library.css";

type Params = { params: Promise<{ id: string }> };
export const dynamicParams = false;
export function generateStaticParams() {
  return library().pub.map((p) => ({ id: p.id }));
}
export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { id } = await params;
  const p = library().pub.find((x) => x.id === id);
  return { title: `${p?.org ?? ""}: ${p?.w ?? ""} · 공개 AX 사례` };
}

/** 굵은 이름마다 아이콘 */
const PART_ICON: Record<string, string> = {
  문제: "circle-exclamation-point",
  "공개된 업무": "briefcase",
  "확인된 흐름": "workflow",
  "업무와 판단": "scale",
  "AI의 역할": "bot",
  "사람의 판단": "user-check",
  "운영 경계": "shield",
  "운영 통제": "shield-check",
  "평가 방식": "gauge",
  "기존 기록의 흐름": "clock",
  "초기 흐름과 발표": "clock",
};
const RESULT = ["공개 결과", "이후 확인된 변화"];
const LEARN = ["로드맵에서 배울 점", "실습에서 물을 점"];
const EVID = ["근거와 한계", "주장 기록"];
const host = (u: string) => {
  try {
    return new URL(u).hostname.replace(/^www\./, "");
  } catch {
    return u;
  }
};

export default async function PublicCasePage({ params }: Params) {
  const { id } = await params;
  const lib = library();
  const r = roadmap();
  const k = lib.pub.findIndex((x) => x.id === id);
  const p = lib.pub[k];
  const prev = lib.pub[k - 1];
  const next = lib.pub[k + 1];
  const src = "research/public-ax-cases.md";
  const md = (s: string) => renderRoadmapMd(src, s);
  const steps = p.parts.filter((x) => ![...RESULT, ...LEARN, ...EVID].includes(x.label));
  const results = p.parts.filter((x) => RESULT.includes(x.label));
  const learns = p.parts.filter((x) => LEARN.includes(x.label));
  const evid = p.parts.filter((x) => EVID.includes(x.label));
  const [stepsH, resultsH, learnsH, evidH, notesH] = await Promise.all([steps, results, learns, evid, p.notes].map((xs) => Promise.all(xs.map((x) => md(x.md)))));
  const related = p.related.map((cid) => r.cases.find((x) => x.id === cid)).filter((x) => !!x);
  const same = lib.pub.filter((x) => x.ind === p.ind && x.id !== p.id).slice(0, 4);

  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["공개 AX 사례", "/library/public/"], [p.org]]} />
      <header className="lb-hero">
        <OrgMark id={p.id} org={p.org} size="lg" />
        <div>
          <p className="lb-hero-e">
            <span className="mono">{p.id}</span> · {regionKo(p.region)} · {IND_KO[p.ind] ?? p.ind}
          </p>
          <h1>{p.org}</h1>
          <p className="lb-hero-w">{p.w}</p>
        </div>
      </header>

      <div className="lb-axes">
        <div className="tile">
          <small>도입 단계</small>
          <span className={`badge lg ${stageTone(p.stage)}`}>{lib.stageKo(p.stage)}</span>
        </div>
        <div className="tile">
          <small>성과 검증</small>
          <span className={`badge lg ${verifyTone(p.verify)}`}>{lib.verifyKo(p.verify)}</span>
        </div>
        <div className="tile">
          <small>출처</small>
          <span className="badge lg">{lib.sourceKo(p.source)}</span>
        </div>
        <div className="tile">
          <small>원문 확인일</small>
          <b className="lb-num">{p.checked}</b>
        </div>
      </div>

      {results.length > 0 && (
        <section className="lb-result">
          <Ic n="megaphone" />
          <div>
            <small>회사가 발표한 결과</small>
            {resultsH.map((h, n) => (
              <div key={n} className="prose" dangerouslySetInnerHTML={{ __html: h }} />
            ))}
          </div>
        </section>
      )}

      <section className="sec">
        <SecHead title="업무는 이렇게 흘러가요" />
        <ol className="lb-flow">
          {steps.map((s, n) => (
            <li key={s.label}>
              <span className="lb-flow-i">
                <Ic n={PART_ICON[s.label] ?? "circle-dot"} />
              </span>
              <div>
                <b>{s.label}</b>
                <div className="prose" dangerouslySetInnerHTML={{ __html: stepsH[n] }} />
              </div>
            </li>
          ))}
        </ol>
      </section>

      {learns.length > 0 && (
        <section className="lb-check lb-check-lg">
          <small>
            <Ic n="list-checks" />내 설계에서 볼 것
          </small>
          {learnsH.map((h, n) => (
            <div key={n} className="prose" dangerouslySetInnerHTML={{ __html: h }} />
          ))}
        </section>
      )}

      <section className="sec">
        <SecHead title="근거와 한계" />
        {evidH.map((h, n) => (
          <div key={n} className="prose lb-evid" dangerouslySetInnerHTML={{ __html: h }} />
        ))}
        {p.notes.length > 0 && (
          <More label={`추가 확인과 정정 ${p.notes.length}건`}>
            <ul className="lb-notes">
              {p.notes.map((x, n) => (
                <li key={n}>
                  {x.kind && <span className="badge">{x.kind}</span>}
                  <div className="prose" dangerouslySetInnerHTML={{ __html: notesH[n] }} />
                </li>
              ))}
            </ul>
          </More>
        )}
        <div className="lb-links">
          {p.urls.map((u) => (
            <a key={u} href={u} target="_blank" rel="noopener">
              <ExternalLink aria-hidden="true" />
              <span>
                <b>{host(u)}</b>
                <small>{decodeURI(u.replace(/^https?:\/\/[^/]+/, "")).slice(0, 60) || "/"}</small>
              </span>
            </a>
          ))}
        </div>
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

      {same.length > 0 && (
        <section className="sec">
          <SecHead title={`같은 산업의 공개 사례 (${IND_KO[p.ind] ?? p.ind})`} />
          <div className="lb-orgs lb-orgs-sm">
            {same.map((x) => (
              <Link key={x.id} href={`/library/public/${x.id}/`} className="lb-org-card">
                <OrgMark id={x.id} org={x.org} size="sm" />
                <span className="lb-org-b">
                  <b>{x.org}</b>
                  <span className="lb-org-w">{x.w}</span>
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}

      <p className="lb-note">
        원본: <a className="lk" href={ghBlob(src)}>research/public-ax-cases.md</a>. 주장마다 날짜, 표본, 방법, 한계는 <a className="lk" href={ghBlob("research/public-ax-cases.json")}>public-ax-cases.json</a>에 있어요.
      </p>

      <nav className="pn" aria-label="이전, 다음 공개 사례">
        {prev ? (
          <Link href={`/library/public/${prev.id}/`}>
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
          <Link className="r" href={`/library/public/${next.id}/`}>
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
