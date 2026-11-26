"use client";
import Link from "next/link";
import { useState } from "react";
import Level from "./Level";
import Thumb from "./Thumb";
import type { Stage, TrackKey } from "@/lib/content";
import type { Logo } from "@/lib/logos";
import { plainInline } from "@/lib/inline";

type Filter = { key: TrackKey | "all"; label: string; count: number; logo?: Logo };
type Props = { stages: Stage[]; filters: Filter[]; fresh: string[]; logos: Record<string, Logo[]> };

/** 단계별 챕터 카드. 분류 버튼으로 걸러요. */
export default function CurriculumList({ stages, filters, fresh, logos }: Props) {
  const [f, setF] = useState<TrackKey | "all">("all");
  const show = (k: TrackKey) => f === "all" || f === k;
  return (
    <>
      <div className="curr-tools">
        <div className="filter" role="group" aria-label="분류">
          {filters.map((x) => (
            <button key={x.key} type="button" aria-pressed={f === x.key} onClick={() => setF(x.key)}>
              {x.logo && (
                <span className="fl" style={{ background: x.logo.hex }} aria-hidden="true">
                  {x.logo.path ? (
                    <svg viewBox="0 0 24 24" width="11" height="11" fill="#fff">
                      <path d={x.logo.path} />
                    </svg>
                  ) : null}
                </span>
              )}
              {x.label}
              <small>{x.count}</small>
            </button>
          ))}
        </div>
        <div className="lvl-key" aria-label="레벨 표시">
          <Level level="입문" title={false} />
          <Level level="기초" title={false} />
          <Level level="응용" title={false} />
        </div>
      </div>
      {stages.map((s) => {
        const list = s.groups.flatMap((g) => g.chapters.map((c) => ({ ...c, group: g.title }))).filter((c) => show(c.trackKey));
        return (
          <section className="stage" id={`stage-${s.no}`} key={s.no} hidden={!list.length}>
            <header className="stage-h">
              <span className="step">{s.no}</span>
              <div>
                <h3>{s.title}</h3>
                <p>{s.summary}</p>
              </div>
              <small>
                {s.from}–{s.to} · {s.count}챕터
              </small>
            </header>
            <div className="cards">
              {list.map((c) => (
                <Link className="card" key={c.dir} href={`/chapters/${c.dir}/`} title={plainInline(c.goal)}>
                  <Thumb no={c.no} logos={logos[c.dir]} label={c.group} kw={c.keyword} />
                  <div className="card-b">
                    <b>
                      {c.title}
                      {fresh.includes(c.dir) && <span className="new-dot">NEW</span>}
                    </b>
                    <span className="card-m">
                      <Level level={c.level} />
                      <span className={`chip ${c.trackKey}`}>{c.track}</span>
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        );
      })}
    </>
  );
}
