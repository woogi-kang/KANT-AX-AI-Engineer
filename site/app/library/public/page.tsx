import type { Metadata } from "next";
import Link from "next/link";
import { ChevronDown, ExternalLink } from "lucide-react";
import { roadmap, ghBlob } from "@/lib/roadmap";
import { renderRoadmapMd } from "@/lib/markdown";
import { library, homeOf, regionKo, IND_KO } from "@/lib/library";
import { caseIcon } from "@/lib/site";
import { Crumb, Ic, Ict, More, PageHead } from "@/components/ui";
import LibTiles from "@/components/LibTiles";
import LibFilter from "@/components/LibFilter";
import "../library.css";

export const metadata: Metadata = { title: "공개 AX 사례" };

const host = (u: string) => {
  try {
    return new URL(u).hostname.replace(/^www\./, "");
  } catch {
    return u;
  }
};
/** 같은 사이트 주소는 하나만 */
const hosts = (us: string[]) => us.filter((u, k) => us.findIndex((x) => host(x) === host(u)) === k);
const count = <T,>(xs: T[], f: (x: T) => string) => {
  const m = new Map<string, number>();
  for (const x of xs) m.set(f(x), (m.get(f(x)) ?? 0) + 1);
  return [...m.entries()].sort((a, b) => b[1] - a[1]);
};

export default async function PublicPage() {
  const lib = library();
  const r = roadmap();
  const P = lib.pub;
  const src = "research/public-ax-cases.md";
  const html = await Promise.all(P.map((p) => renderRoadmapMd(src, p.md)));
  const axesHtml = await renderRoadmapMd(src, lib.pubMeta.axesMd);
  const kr = P.filter((p) => p.region === "KR").length;
  const STAGE_ORDER = ["operation", "limited-operation", "pilot", "adjusted-operation", "unknown"];
  const VERIFY_ORDER = ["cross-checked", "self-reported", "none"];
  const stages = count(P, (p) => p.stage).sort((a, b) => STAGE_ORDER.indexOf(a[0]) - STAGE_ORDER.indexOf(b[0]));
  const verifies = count(P, (p) => p.verify).sort((a, b) => VERIFY_ORDER.indexOf(a[0]) - VERIFY_ORDER.indexOf(b[0]));
  const inds = count(P, (p) => p.ind);
  const tone = (v: string) => (v === "cross-checked" ? "ok" : v === "self-reported" ? "warn" : "");

  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["공개 AX 사례"]]} />
      <PageHead icon={<Ict n="file-check" size="lg" />} title="공개 AX 사례" lede="회사와 기관이 스스로 공개한 AX 업무 사례예요. 사례마다 출처와 확인일이 있어요." />
      <LibTiles on="public" />

      <div className="tiles t4 lb-facts" style={{ marginTop: 24 }}>
        <div className="tile">
          <span className="num">{P.filter((p) => p.stage === "operation").length}</span>
          <small>운영 단계로 발표한 사례</small>
        </div>
        <div className="tile">
          <span className="num">
            {kr}
            <span className="lb-slash">/</span>
            {P.length - kr}
          </span>
          <small>국내 / 해외</small>
        </div>
        <div className="tile">
          <span className="num">{P.filter((p) => p.verify === "self-reported").length}</span>
          <small>성과를 자체 발표한 사례</small>
        </div>
        <div className="tile">
          <b className="mono lb-date">{lib.pubMeta.updated}</b>
          <small>원문 확인일 · 처음 목록 {lib.pubMeta.baseline || lib.pubMeta.verified}</small>
        </div>
      </div>
      <p className="lb-warn">
        <Ic n="info" />
        운영이나 자체 발표는 독립 검증이 아니에요. 이 레포가 조직의 운영을 실사하거나 성과를 재현하지 않았어요.
      </p>
      <More label="근거를 읽는 세 축(출처, 도입, 성과)">
        <div className="prose" dangerouslySetInnerHTML={{ __html: axesHtml }} />
      </More>

      <LibFilter
        target="#pub-list"
        search="조직, 업무 찾기"
        unit="건"
        groups={[
          { key: "home", label: "국내/해외", options: [{ value: "kr", label: "국내", count: kr }, { value: "abroad", label: "해외", count: P.length - kr }] },
          { key: "stage", label: "도입 단계", options: stages.map(([s, n]) => ({ value: s, label: lib.stageKo(s), count: n })) },
          { key: "verify", label: "성과 검증", options: verifies.map(([v, n]) => ({ value: v, label: lib.verifyKo(v), count: n })) },
          { key: "ind", label: "산업", kind: "select", options: inds.map(([i, n]) => ({ value: i, label: IND_KO[i] ?? i, count: n })) },
        ]}
      />

      <div className="lb-cards" id="pub-list">
        {P.map((p, n) => (
          <article key={p.id} id={p.id} className="lb-card" data-item="" data-home={homeOf(p.region)} data-stage={p.stage} data-verify={p.verify} data-ind={p.ind} data-q={`${p.id} ${p.org} ${p.w} ${IND_KO[p.ind] ?? ""}`}>
            <div className="lb-card-h">
              <span className="mono muted">{p.id}</span>
              <span className="badge">{regionKo(p.region)}</span>
              <span className="badge">{IND_KO[p.ind] ?? p.ind}</span>
            </div>
            <b className="lb-org">{p.org}</b>
            <p className="lb-w">{p.w}</p>
            <div className="lb-kv">
              <span>
                <small>도입</small>
                <span className="badge ac">{lib.stageKo(p.stage)}</span>
              </span>
              <span>
                <small>성과</small>
                <span className={`badge ${tone(p.verify)}`}>{lib.verifyKo(p.verify)}</span>
              </span>
              <span>
                <small>출처</small>
                <span className="badge">{lib.sourceKo(p.source)}</span>
              </span>
            </div>
            <div className="lb-card-f">
              <span className="muted">
                확인 <span className="mono">{p.checked}</span>
              </span>
              <span className="lb-srcs">
                {hosts(p.urls).slice(0, 2).map((u) => (
                  <a key={u} href={u} target="_blank" rel="noopener">
                    {host(u)}
                    <ExternalLink aria-hidden="true" />
                  </a>
                ))}
                {hosts(p.urls).length > 2 && <span className="muted">외 {hosts(p.urls).length - 2}곳</span>}
              </span>
            </div>
            {p.related.length > 0 && (
              <div className="chips">
                {p.related.map((id) => {
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
            {p.md && (
              <details className="lb-det">
                <summary>
                  흐름, 사람의 판단, 근거와 한계
                  <ChevronDown aria-hidden="true" />
                </summary>
                <div className="prose" dangerouslySetInnerHTML={{ __html: html[n] }} />
              </details>
            )}
          </article>
        ))}
      </div>
      <p className="lb-note">
        원본: <a className="lk" href={ghBlob(src)}>research/public-ax-cases.md</a> · <a className="lk" href={ghBlob("research/public-ax-cases.json")}>public-ax-cases.json</a>. 주장마다 날짜, 표본, 방법, 한계는 JSON에 있어요.
      </p>
    </>
  );
}
