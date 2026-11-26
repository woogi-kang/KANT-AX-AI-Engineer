"use client";
import Link from "next/link";
import { useState } from "react";
import { ChevronRight } from "lucide-react";
import Level from "./Level";
import type { Stage, TrackKey } from "@/lib/content";
import { renderInline } from "@/lib/inline";

type Props = { stages: Stage[]; filters: { key: TrackKey | "all"; label: string; count: number }[]; fresh: string[] };

/** 단계, 묶음, 챕터 목록. 분류 버튼으로 거르고 단계를 접어요. */
export default function CurriculumList({ stages, filters, fresh }: Props) {
  const [f, setF] = useState<TrackKey | "all">("all");
  const [closed, setClosed] = useState<Set<number>>(new Set());
  const show = (k: TrackKey) => f === "all" || f === k;
  const toggle = (n: number) =>
    setClosed((s) => {
      const t = new Set(s);
      if (t.has(n)) t.delete(n);
      else t.add(n);
      return t;
    });
  return (
    <>
      <div className="curr-tools">
        <div className="filter" role="group" aria-label="분류">
          {filters.map((x) => (
            <button key={x.key} type="button" aria-pressed={f === x.key} onClick={() => setF(x.key)}>
              {x.label} {x.count}
            </button>
          ))}
        </div>
        <div className="lvl-key" aria-label="레벨 표시">
          <span>레벨</span>
          <Level level="입문" title={false} />
          <Level level="기초" title={false} />
          <Level level="응용" title={false} />
        </div>
      </div>
      {stages.map((s) => {
        const any = s.groups.some((g) => g.chapters.some((c) => show(c.trackKey)));
        const isClosed = closed.has(s.no);
        return (
          <section className="stage" id={`stage-${s.no}`} key={s.no} hidden={!any} data-closed={isClosed || undefined}>
            <header>
              <button className="stage-tg" type="button" aria-expanded={!isClosed} aria-label={`${s.title} ${isClosed ? "펴기" : "접기"}`} onClick={() => toggle(s.no)}>
                <ChevronRight className="i" />
              </button>
              <span className="k">{s.no}단계</span>
              <h3>{s.title}</h3>
              <small>
                {s.from}–{s.to} · {s.count}챕터 · 묶음 {s.groups.length}개
              </small>
              <p>{s.summary}</p>
            </header>
            <div className="stage-body">
              {s.groups.map((g) => (
                <div className="grp-b" key={g.title} hidden={!g.chapters.some((c) => show(c.trackKey))}>
                  <h4>
                    {g.title}
                    <span>{g.from === g.to ? g.from : `${g.from}–${g.to}`}</span>
                  </h4>
                  <div className="ch-list">
                    {g.chapters.map((c) => (
                      <Link className="ch-row" key={c.dir} href={`/chapters/${c.dir}/`} hidden={!show(c.trackKey)}>
                        <span className="no" style={{ color: `var(--t-${c.trackKey})` }}>
                          {c.no}
                        </span>
                        <div>
                          <div className="t">
                            {c.title}
                            {fresh.includes(c.dir) && <span className="new-dot">새 챕터</span>}
                          </div>
                          <div className="g" dangerouslySetInnerHTML={{ __html: renderInline(c.goal) }} />
                        </div>
                        <span className="meta">
                          <Level level={c.level} />
                          <span className={`chip ${c.trackKey}`}>{c.track}</span>
                        </span>
                      </Link>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        );
      })}
    </>
  );
}
