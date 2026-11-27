import type { Metadata } from "next";
import Link from "next/link";
import { ChevronDown, ExternalLink } from "lucide-react";
import { ghBlob } from "@/lib/roadmap";
import { renderRoadmapMd } from "@/lib/markdown";
import { library } from "@/lib/library";
import { Crumb, Ic, Ict, More, PageHead, SecHead } from "@/components/ui";
import LibTiles from "@/components/LibTiles";
import LibFilter from "@/components/LibFilter";
import OrgMark from "@/components/OrgMark";
import "../library.css";

export const metadata: Metadata = { title: "채용 현황" };

const tally = (xs: string[]) => {
  const m = new Map<string, number>();
  for (const x of xs) m.set(x, (m.get(x) ?? 0) + 1);
  return [...m.entries()].sort((a, b) => b[1] - a[1]);
};
const ROLE_ORDER = ["ax", "ai-agent", "fde"];
const ym = (m: string) => `${m.slice(0, 4)}년 ${+m.slice(5, 7)}월`;

function Bars({ items, total, label }: { items: [string, number][]; total: number; label: string }) {
  const max = Math.max(...items.map(([, n]) => n));
  return (
    <div className="lb-bars" role="img" aria-label={`${label}: ${items.map(([k, n]) => `${k} ${n}건`).join(", ")}`}>
      {items.map(([k, n]) => (
        <div key={k} className="lb-bar">
          <span className="lb-bl">{k}</span>
          <span className="lb-track">
            <i style={{ width: `${(n / max) * 100}%` }} />
          </span>
          <b>
            {n}
            <small> {Math.round((n / total) * 100)}%</small>
          </b>
        </div>
      ))}
    </div>
  );
}

export default async function JobsPage() {
  const lib = library();
  const H = lib.hiring;
  const m = H.at(-1);
  const src = "research/hiring-monthly/README.md";
  const [scopeHtml, rolesHtml, statusHtml, limitsHtml] = await Promise.all([lib.hiringMd.scope, lib.hiringMd.roles, lib.hiringMd.status, lib.hiringMd.limits].map((s) => renderRoadmapMd(src, s)));
  if (!m) {
    return (
      <>
        <Crumb items={[["사례와 자료", "/library/"], ["채용 현황"]]} />
        <PageHead icon={<Ict n="chart-column" size="lg" />} title="채용 현황" />
        <LibTiles on="jobs" />
        <p className="soonbox">아직 모은 달이 없어요.</p>
      </>
    );
  }
  const P = m.postings;
  const open = P.filter((p) => p.open).length;
  const roles = ROLE_ORDER.filter((r) => P.some((p) => p.role === r));
  const roleRows = roles.map((r) => {
    const ps = P.filter((p) => p.role === r);
    return { r, n: ps.length, open: ps.filter((p) => p.open).length };
  });
  const roleMax = Math.max(...roleRows.map((x) => x.n));
  const region = tally(P.map((p) => (p.location || "미확인").split(" ")[0]));
  const regionTop = [...region.slice(0, 4), ...(region.length > 4 ? [["그 밖", region.slice(4).reduce((a, [, n]) => a + n, 0)] as [string, number]] : [])];
  const emp = tally(P.map((p) => p.employment.split("·")[0].replace(/\(.*\)/, "")));
  const tags = tally(P.flatMap((p) => p.tags));
  const collected = m.platforms.filter((p) => p.collected).map((p) => p.name);

  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["채용 현황"]]} />
      <PageHead icon={<Ict n="chart-column" size="lg" />} title="채용 현황" lede="국내에 AX, AI Agent, FDE 공고가 얼마나, 어떤 모양으로 올라오는지 달마다 모아요." />
      <LibTiles on="jobs" />

      <section className="sec">
        <div className="lb-month">
          <div className="fchips" role="group" aria-label="모은 달">
            {H.map((h) => (
              <span key={h.month} className={h === m ? "lb-mon on" : "lb-mon"}>
                {ym(h.month)}
              </span>
            ))}
          </div>
          <span className="muted lb-num">
            접수 시작 {m.from} ~ {m.to} · 확인 {m.checked} · {collected.join(", ")}
          </span>
        </div>
        <div className="lb-stat">
          <span>
            <b className="lb-ok">{open}</b>모집 중
          </span>
          <span>
            <b>{P.length - open}</b>마감
          </span>
          <span>
            <b>{m.excluded}</b>범위 밖이라 뺀 공고
          </span>
          <span className="lb-stat-d">모집 상태는 {m.checked} 기준 · 보류 {m.held}건</span>
        </div>
        <p className="lb-warn">
          <Ic n="info" />
          재게시와 프로젝트 공고가 섞여 있어 고유 채용 수가 아니에요. {collected.join(", ")}에서만 모아서 시장 전체 규모나 증감을 뜻하지 않아요.
        </p>
      </section>

      {H.length > 1 && (
        <section className="sec">
          <SecHead title="달별 공고 수" />
          <Bars items={H.map((h) => [ym(h.month), h.postings.length] as [string, number])} total={Math.max(...H.map((h) => h.postings.length))} label="달별 공고 수" />
        </section>
      )}

      <section className="sec">
        <SecHead title="직무 유형별 공고" right={<span className="cnt">{ym(m.month)}</span>} />
        <div className="lb-roles" role="img" aria-label={roleRows.map((x) => `${lib.ROLE_KO[x.r]} ${x.n}건 중 모집 중 ${x.open}건`).join(", ")}>
          {roleRows.map((x) => (
            <div key={x.r} className="lb-role">
              <b>{lib.ROLE_KO[x.r] ?? x.r}</b>
              <span className="lb-track lg">
                <i className="o" style={{ width: `${(x.open / roleMax) * 100}%` }} />
                <i className="c" style={{ width: `${((x.n - x.open) / roleMax) * 100}%` }} />
              </span>
              <span className="lb-rn">
                <b>{x.n}</b>
                <small>모집 중 {x.open}</small>
              </span>
            </div>
          ))}
        </div>
        <p className="lb-legend">
          <span className="sw now" />
          모집 중 <span className="sw off" />
          마감
        </p>
        <p className="lb-note">제목에 FDE가 있으면 FDE, 그다음 Agent·에이전트가 있으면 AI Agent, 나머지는 AX로 나눴어요.</p>
        <div className="tiles t2 lb-2">
          <div className="tile">
            <h3>근무지(시·도)</h3>
            <Bars items={regionTop} total={P.length} label="근무지" />
          </div>
          <div className="tile">
            <h3>고용 형태(첫 번째 표기)</h3>
            <Bars items={emp.slice(0, 5)} total={P.length} label="고용 형태" />
          </div>
        </div>
        {tags.length > 0 && (
          <p className="lb-note">
            함께 섞인 공고: {tags.map(([t, n]) => `${lib.TAG_KO[t] ?? t} ${n}건`).join(", ")}
          </p>
        )}
      </section>

      <section className="sec">
        <SecHead title="공고 목록" right={<a href={ghBlob(`research/hiring-monthly/${m.month}.md`)}>원문 목록</a>} />
        <LibFilter
          target="#job-list"
          search="기업, 공고 제목, 근무지 찾기"
          unit="건"
          groups={[
            { key: "role", label: "유형", options: roleRows.map((x) => ({ value: x.r, label: lib.ROLE_KO[x.r] ?? x.r, count: x.n })) },
            { key: "st", label: "상태", options: [{ value: "open", label: "모집 중", count: open }, { value: "closed", label: "마감", count: P.length - open }] },
          ]}
        />
        <ul className="lb-jobs" id="job-list">
          {P.map((p) => (
            <li key={p.id} className="lb-job" data-item="" data-role={p.role} data-st={p.open ? "open" : "closed"} data-q={`${p.company} ${p.title} ${p.location} ${p.experience} ${p.employment}`}>
              <OrgMark id="" org={p.company} size="sm" />
              <div className="lb-job-b">
              <div className="lb-job-h">
                <span className="badge">{lib.ROLE_KO[p.role] ?? p.role}</span>
                <span className={p.open ? "badge ok" : "badge"}>{p.open ? "모집 중" : "마감"}</span>
                {p.tags.map((t) => (
                  <span key={t} className="badge warn">
                    {lib.TAG_KO[t] ?? t}
                  </span>
                ))}
                <span className="mono muted lb-jid">{p.id}</span>
              </div>
              {p.url ? (
                <a className="lb-job-t" href={p.url} target="_blank" rel="noopener">
                  {p.title}
                  <ExternalLink aria-hidden="true" />
                </a>
              ) : (
                <span className="lb-job-t">{p.title}</span>
              )}
              <span className="lb-job-m">
                <b>{p.company}</b>
                <span>{p.location}</span>
                <span>{p.experience}</span>
                <span>{p.employment}</span>
                <span className="lb-num">마감 {p.deadline || "미확인"}</span>
              </span>
              </div>
            </li>
          ))}
        </ul>
        <p className="lb-note">상태는 {m.checked}에 확인한 값이에요. 지금은 마감됐을 수 있으니 공고 페이지에서 다시 확인해요.</p>
      </section>

      <section className="sec">
        <SecHead title="어떻게 모았나요" right={<a href={ghBlob(src)}>수집 기준 원문</a>} />
        <div className="tw">
          <table>
            <thead>
              <tr>
                <th>플랫폼</th>
                <th>{ym(m.month)}</th>
                <th>메모</th>
              </tr>
            </thead>
            <tbody>
              {m.platforms.map((p) => (
                <tr key={p.name}>
                  <td>{p.name}</td>
                  <td>{p.collected ? <span className="badge ok">수집</span> : <span className="badge">미수집</span>}</td>
                  <td>{p.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="lb-note">검색어: {m.queries.join(", ")}</p>
        <div className="doc">
          {[
            ["한계", limitsHtml],
            ["수집 범위", scopeHtml],
            ["직무 범위", rolesHtml],
            ["분류와 상태", statusHtml],
          ].map(([t, h], n) => (
            <details key={t} open={n === 0}>
              <summary>
                {t}
                <ChevronDown aria-hidden="true" />
              </summary>
              <div className="in prose" dangerouslySetInnerHTML={{ __html: h }} />
            </details>
          ))}
        </div>
        <More label="공고 하나하나의 책임과 요건을 읽고 싶다면">
          <p>
            로드맵 레포의{" "}
            <a className="lk" href={ghBlob("research/hiring-signals.md")}>
              공고로 보는 AX 직무 해설
            </a>
            에 있어요. 역할을 먼저 보려면{" "}
            <Link className="lk" href="/roadmap/">
              로드맵 1단계
            </Link>
            부터 봐요.
          </p>
        </More>
      </section>
    </>
  );
}
