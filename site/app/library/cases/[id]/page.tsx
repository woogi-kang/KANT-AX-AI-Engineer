import type { Metadata } from "next";
import Link from "next/link";
import { ChevronDown, ChevronLeft, ChevronRight, ExternalLink, Play } from "lucide-react";
import { roadmap, ghBlob, readRmJson, ROADMAP_URL } from "@/lib/roadmap";
import { renderRoadmapMd } from "@/lib/markdown";
import { autonomyLevels, autonomyRange, caseDetail, library, projectStages } from "@/lib/library";
import { caseIcon } from "@/lib/site";
import { Crumb, Diff, Ic, Ict, More, PageHead, SecHead } from "@/components/ui";
import CopyText from "@/components/CopyText";
import OrgMark from "@/components/OrgMark";
import "../../library.css";

type Params = { params: Promise<{ id: string }> };
export const dynamicParams = false;
export function generateStaticParams() {
  return roadmap().cases.map((c) => ({ id: c.id }));
}
export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { id } = await params;
  const c = roadmap().cases.find((x) => x.id === id);
  return { title: `${c?.t ?? ""} · 업무 사례` };
}

function Cmd({ code }: { code: string }) {
  return (
    <div className="lb-cmd">
      <pre>
        <code>{code}</code>
      </pre>
      <CopyText text={code} className="lb-cp" label="복사" done="복사했어요" />
    </div>
  );
}

export default async function CasePage({ params }: Params) {
  const c = caseDetail((await params).id);
  const r = roadmap();
  const lib = library();
  const md = (s: string) => renderRoadmapMd(c.path, s);
  const A = autonomyLevels();
  const P = projectStages();
  const cur = c.boundary[0];
  const goal = c.boundary[1];
  const aNow = autonomyRange(c.json.current_autonomy);
  const aGoal = autonomyRange(c.json.designed_autonomy);
  // 추천 학습 순서(case.json learning_order)로 이전, 다음
    const ordered = r.cases.map((x) => ({ x, n: readRmJson<{ learning_order: number }>(`case-studies/${x.id}/case.json`).learning_order })).sort((a, b) => a.n - b.n);
  const k = ordered.findIndex((o) => o.x.id === c.id);
  const prev = ordered[k - 1]?.x;
  const next = ordered[k + 1]?.x;
  const before = c.json.recommended_after.map((id) => r.cases.find((x) => x.id === id)).filter((x) => !!x);
  const pubs = c.publicIds.map((id) => lib.pub.find((p) => p.id === id)!);
  const fails = c.failureIds.map((id) => lib.fails.find((f) => f.id === id)!);
  const [introHtml, failHtml, limitsHtml] = await Promise.all([md(c.intro), md(c.failureNote.replace(/^> ?/gm, "")), c.limits ? md(c.limits.body) : ""]);
  const restHtml = await Promise.all(c.rest.map((s) => md(s.body)));
  const rbHtml = c.runbook ? await Promise.all(c.runbook.rest.map((s) => renderRoadmapMd(c.runbook!.path, s.body))) : [];

  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["업무 사례", "/library/"], [c.t]]} />
      <PageHead icon={<Ict n={caseIcon(c.area)} size="lg" />} eyebrow={`${c.area} · ${c.industry} · 추천 순서 ${c.json.learning_order}`} title={c.t} />
      {c.runnable && (
        <p className="lb-runline">
          <span className="run">
            <Play aria-hidden="true" />
            실행 예제
          </span>
          내 컴퓨터에서 그대로 돌려 볼 수 있는 사례예요.
        </p>
      )}

      <div className="tiles t4 lb-facts">
        <div className="tile">
          <small>난이도</small>
          <span className="lb-big">
            {c.diff}
            <small> / 5</small>
          </span>
          <Diff v={c.diff} />
        </div>
        <div className="tile">
          <small>위험</small>
          <span className={`lb-big lb-risk-${c.risk === "높음" ? "h" : c.risk === "보통" ? "m" : "l"}`}>{c.risk}</span>
        </div>
        <div className="tile">
          <small>지금 공개한 근거</small>
          <b>{c.ev}</b>
        </div>
        <div className="tile">
          <small>확인일</small>
          <b className="lb-num lb-date">{c.json.verified_at}</b>
        </div>
      </div>

      {c.runbook && (
        <section className="sec lb-try">
          <SecHead title="따라 해 보기" right={<a href={ghBlob(c.runbook.path)}>실행 안내 원문</a>} />
          <p className="lb-note">파이썬 표준 라이브러리만 써요. 외부 API, 모델, 계정, 네트워크가 없어도 돼요. 명령은 레포 맨 위 폴더에서 쳐요.</p>
          <ol className="lb-steps">
            <li>
              <b>로드맵 레포 받기</b>
              <Cmd code={`git clone ${ROADMAP_URL}.git\ncd ax-engineer-roadmap`} />
            </li>
            {c.runbook.run[0] && (
              <li>
                <b>실행하기</b>
                <small>성공하면 artifacts/ 폴더에 분류 결과, 검토 큐, 업무 제안, 평가 결과, 대시보드가 생겨요. 기대 결과와 하나라도 다르면 종료 코드 1로 끝나요.</small>
                <Cmd code={c.runbook.run[0]} />
              </li>
            )}
            {c.runbook.run[1] && (
              <li>
                <b>올라간 결과와 같은지 확인하기</b>
                <small>깨끗한 임시 폴더에서 다시 만든 결과가 레포에 올라간 결과와 같은지 봐요.</small>
                <Cmd code={c.runbook.run[1]} />
              </li>
            )}
            {c.runbook.test[0] && (
              <li>
                <b>테스트하기</b>
                <Cmd code={c.runbook.test[0]} />
              </li>
            )}
          </ol>
          {c.summary && (
            <div className="lb-res">
              <h3>
                레포에 올라간 실행 결과 <span className="muted mono">{c.summary.asOf}</span>
              </h3>
              <div className="tiles t3">
                <div className="tile">
                  <span className="num">{c.summary.input}</span>
                  <small>넣은 합성 VOC</small>
                </div>
                <div className="tile">
                  <span className="num">{c.summary.proposals}</span>
                  <small>만든 업무 제안</small>
                </div>
                <div className="tile">
                  <span className={`num ${c.summary.passed ? "lb-ok" : "lb-err"}`}>{c.summary.passed ? "통과" : "실패"}</span>
                  <small>평가</small>
                </div>
              </div>
              <div className="lb-bars" role="img" aria-label={`처리 상태: ${Object.entries(c.summary.status).map(([s, n]) => `${s} ${n}건`).join(", ")}`}>
                {Object.entries(c.summary.status)
                  .sort((a, b) => b[1] - a[1])
                  .map(([s, n]) => (
                    <div key={s} className="lb-bar">
                      <code>{s}</code>
                      <span className="lb-track">
                        <i style={{ width: `${(n / c.summary!.input) * 100}%` }} />
                      </span>
                      <b>{n}</b>
                    </div>
                  ))}
              </div>
              <p className="lb-note">레포의 artifacts/run-summary.json 값이에요. 합성 입력이라 실제 회사 VOC의 분포를 뜻하지 않아요.</p>
              {c.dashboard && (
                <More label="결과 대시보드 보기">
                  <figure className="lb-fig">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={c.dashboard} alt="실행 결과 대시보드 화면" loading="lazy" />
                    <figcaption>레포에 올라간 결과 대시보드(artifacts/dashboard.png)</figcaption>
                  </figure>
                </More>
              )}
            </div>
          )}
          {c.runbook.rest.length > 0 && (
            <div className="doc">
              {c.runbook.rest.map((s, n) => (
                <details key={s.title}>
                  <summary>
                    {s.title}
                    <ChevronDown aria-hidden="true" />
                  </summary>
                  <div className="in prose" dangerouslySetInnerHTML={{ __html: rbHtml[n] }} />
                </details>
              ))}
            </div>
          )}
        </section>
      )}

      <section className="sec">
        <SecHead title="AI가 어디까지 하나요" />
        <div className="lb-track5" role="list" aria-label="자율성 수준">
          {A.map((a) => {
            const n = +a.lv.slice(1);
            const st = aNow.includes(n) ? "now" : aGoal.includes(n) ? "goal" : "";
            return (
              <div key={a.lv} role="listitem" className={`lb-step ${st}`}>
                <b className="mono">{a.lv}</b>
                <span>{a.ai}</span>
                <small>{a.run}</small>
                {aNow.includes(n) && <em>지금</em>}
                {!aNow.includes(n) && aGoal.includes(n) && <em>목표</em>}
              </div>
            );
          })}
        </div>
        <SecHead title="프로젝트 단계" as="h3" />
        <div className="lb-track5" role="list" aria-label="프로젝트 단계">
          {P.map((p) => {
            const done = c.json.implemented_project_stages.includes(p.no);
            const goalP = c.json.designed_project_stages.includes(p.no);
            return (
              <div key={p.no} role="listitem" className={`lb-step ${done ? "now" : goalP ? "goal" : "off"}`}>
                <b className="mono">P{p.no}</b>
                <span>{p.t}</span>
                {done && <em>일부 구현</em>}
                {!done && goalP && <em>설계</em>}
                {!done && !goalP && <em className="x">다루지 않음</em>}
              </div>
            );
          })}
        </div>
        <p className="lb-legend">
          <span className="sw now" />
          지금 공개한 결과 <span className="sw goal" />
          설계 목표.{" "}
          <Link className="lk" href="/roadmap/05-execution-contracts/">
            자율성 수준 뜻
          </Link>{" "}
          ·{" "}
          <Link className="lk" href="/roadmap/">
            P1~P5 실습 프로젝트
          </Link>
        </p>
        {cur && goal && (
          <div className="lb-vs">
            <div>
              <small>{cur.label}</small>
              <b>{cur.write}</b>
            </div>
            <ChevronRight aria-hidden="true" />
            <div className="g">
              <small>{goal.label}</small>
              <b>{goal.write}</b>
            </div>
          </div>
        )}
        <SecHead title="쓰는 시스템" as="h3" />
        <div className="chips lb-sys">
          {c.json.systems.map((s) => (
            <span key={s} className="chip">
              {s}
            </span>
          ))}
        </div>
        {before.length > 0 && (
          <>
            <SecHead title="먼저 볼 사례" as="h3" />
            <div className="chips">
              {before.map((b) => (
                <Link key={b!.id} className="chip lb-chip" href={`/library/cases/${b!.id}/`}>
                  <Ic n={caseIcon(b!.area)} />
                  {b!.t}
                </Link>
              ))}
            </div>
          </>
        )}
      </section>

      {c.limits && (
        <section className="sec lb-limit">
          <SecHead title={c.limits.title.replace(/^\d+\.\s*/, "")} />
          <div className="prose" dangerouslySetInnerHTML={{ __html: limitsHtml }} />
        </section>
      )}

      <section className="sec">
        <SecHead title="비슷한 업무의 공개 기록" />
        {fails.length === 0 && pubs.length === 0 && (
          <p className="lb-note">
            연결한 기록이 없어요.{" "}
            <Link className="lk" href="/library/failures/#캡스톤-설계에-쓰는-점검표">
              캡스톤 설계 점검표
            </Link>
            의 여덟 질문으로 점검해요.
          </p>
        )}
        {fails.length > 0 && (
          <>
            <h3 className="lb-h3">멈추거나 되돌린 기록</h3>
            <div className="lb-orgs lb-orgs-sm">
              {fails.map((f) => (
                <Link key={f.id} className="lb-org-card" href={`/library/failures/${f.id}/`}>
                  <OrgMark id={f.id} org={f.org} size="sm" />
                  <span className="lb-org-b">
                    <b>{f.org}</b>
                    <span className="lb-org-m">
                      {f.outcome.map((o) => (
                        <span key={o} className="badge err">
                          {lib.outShort(o)}
                        </span>
                      ))}
                      <span>{f.domain}</span>
                    </span>
                  </span>
                </Link>
              ))}
            </div>
          </>
        )}
        {pubs.length > 0 && (
          <>
            <h3 className="lb-h3">운영하고 있다고 공개한 기록</h3>
            <div className="lb-orgs lb-orgs-sm">
              {pubs.map((p) => (
                <Link key={p.id} className="lb-org-card" href={`/library/public/${p.id}/`}>
                  <OrgMark id={p.id} org={p.org} size="sm" />
                  <span className="lb-org-b">
                    <b>{p.org}</b>
                    <span className="lb-org-w">{p.w}</span>
                  </span>
                </Link>
              ))}
            </div>
          </>
        )}
        {c.failureNote && (
          <More label="실패 사례 점검 원문">
            <div className="prose" dangerouslySetInnerHTML={{ __html: failHtml }} />
          </More>
        )}
      </section>

      <section className="sec">
        <SecHead title="사례 문서" right={<a href={ghBlob(c.path)}>원문</a>} />
        {c.intro && (
          <div className="doc">
            <details open>
              <summary>
                사례 소개
                <ChevronDown aria-hidden="true" />
              </summary>
              <div className="in prose" dangerouslySetInnerHTML={{ __html: introHtml }} />
            </details>
          </div>
        )}
        <div className="doc">
          {c.rest.map((s, n) => (
            <details key={s.title}>
              <summary>
                {s.title}
                <ChevronDown aria-hidden="true" />
              </summary>
              <div className="in prose" dangerouslySetInnerHTML={{ __html: restHtml[n] }} />
            </details>
          ))}
        </div>
        <p className="lb-note">
          로드맵 레포 문서를 그대로 옮겼어요. 고칠 곳은{" "}
          <a className="lk" href={`${ROADMAP_URL}/issues`}>
            로드맵 레포 이슈
            <ExternalLink className="lb-ext" aria-hidden="true" />
          </a>
          로 알려 주세요.
        </p>
      </section>

      <nav className="pn" aria-label="추천 학습 순서로 이전, 다음 사례">
        {prev ? (
          <Link href={`/library/cases/${prev.id}/`}>
            <ChevronLeft className="i" aria-hidden="true" />
            <span>
              <small>이전 사례</small>
              <b>{prev.t}</b>
            </span>
          </Link>
        ) : (
          <span className="empty" />
        )}
        {next ? (
          <Link className="r" href={`/library/cases/${next.id}/`}>
            <ChevronRight className="i" aria-hidden="true" />
            <span>
              <small>다음 사례</small>
              <b>{next.t}</b>
            </span>
          </Link>
        ) : (
          <span className="empty" />
        )}
      </nav>
    </>
  );
}
