import type { Metadata } from "next";
import Link from "next/link";
import { load } from "@/lib/content";
import { roadmap } from "@/lib/roadmap";
import { topicChapters, links } from "@/lib/links";
import { chapterLogo, type LogoKey } from "@/lib/logos";
import { AREA_IC, STAGE_IC, caseIcon } from "@/lib/site";
import { stageCount } from "@/lib/home";
import { Crumb, Diff, Ict, Ic, Logos, More, NumBox, PageHead } from "@/components/ui";
import "./roadmap.css";

export const metadata: Metadata = { title: "로드맵" };

export default function RoadmapPage() {
  const r = roadmap();
  const byNo = new Map(load().chapters.map((c) => [c.no, c]));
  const logos = (nos: string[]): LogoKey[] => [...new Set(nos.map((n) => chapterLogo(n, byNo.get(n)!.track)))];
  return (
    <>
      <Crumb items={[["홈", "/"], ["로드맵"]]} />
      <PageHead icon={<Ict n="route" size="lg" />} title="AX 엔지니어 로드맵" lede="다섯 단계를 차례로 따라가요. 주제 카드의 로고는 먼저 익힐 기초 강의예요." />
      {r.stages.map((s) => (
        <section key={s.no} className="stage" id={`stage-${s.no}`}>
          <div className="th">
            <Ict n={STAGE_IC[s.no]} />
            <div>
              <span className="eyebrow">
                {s.no}단계 · {stageCount(s.no)}
              </span>
              <h2>{s.title}</h2>
            </div>
          </div>
          <div className={`tiles ${s.no === 5 ? "t3" : "t4"}`} style={{ marginTop: 16 }}>
            {s.no === 5
              ? r.cases.map((c) => (
                  <Link key={c.id} className="tp" href={`/library/cases/${c.id}/`}>
                    <span className="hd">
                      <Ict n={caseIcon(c.area)} size="sm" tone="n" />
                      <b>{c.t}</b>
                    </span>
                    <span className="rm-cf">
                      <Diff v={c.diff} />
                      <span className="muted">{c.area}</span>
                      {c.runnable && (
                        <span className="run">
                          <Ic n="play" />
                          실행 예제
                        </span>
                      )}
                    </span>
                  </Link>
                ))
              : s.topics.map((t) => {
                  const nos = topicChapters(t.slug);
                  const soon = links().byTopic[t.slug]?.soon;
                  return (
                    <Link key={t.slug} className="tp" href={`/roadmap/${t.slug}/`}>
                      <span className="hd">
                        {AREA_IC[t.slug] ? <Ict n={AREA_IC[t.slug]} size="sm" /> : <NumBox>{`${s.no}.${t.n}`}</NumBox>}
                        <b>{t.t}</b>
                      </span>
                      {t.kind === "project" && t.q && <small className="rm-q">{t.q}</small>}
                      {nos.length ? <Logos ks={logos(nos)} size={22} /> : t.kind === "area" ? <span className="soon">강의 준비 중{soon ? `: ${soon}` : ""}</span> : null}
                    </Link>
                  );
                })}
          </div>
          <More label={s.checks.length ? "단계 설명과 점검 질문" : "단계 설명"}>
            <p>{s.lede}</p>
            {s.checks.map((c) => (
              <p key={c} style={{ display: "flex", gap: 8 }}>
                <Ic n="circle-check" />
                <span>{c}</span>
              </p>
            ))}
          </More>
        </section>
      ))}
    </>
  );
}
