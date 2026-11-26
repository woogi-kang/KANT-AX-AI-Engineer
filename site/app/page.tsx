import Link from "next/link";
import { ArrowRight } from "lucide-react";
import AppShell from "@/components/AppShell";
import CurriculumList from "@/components/CurriculumList";
import NewsCard from "@/components/NewsCard";
import { TRACKS, isNew, load, news, type TrackKey } from "@/lib/content";
import { renderInline } from "@/lib/inline";

export default function Home() {
  const { stages, chapters, extras } = load();
  const filters: { key: TrackKey | "all"; label: string; count: number }[] = [
    { key: "all", label: "전체", count: chapters.length },
    ...Object.entries(TRACKS).map(([label, key]) => ({ key, label, count: chapters.filter((c) => c.trackKey === key).length })),
  ];
  const fresh = chapters.filter((c) => isNew(c)).map((c) => c.dir);
  return (
    <AppShell current="home">
      <h1 className="page-title">풀스택 AI/AX 엔지니어</h1>
      <p className="lede">
        {chapters.length}챕터를 배우는 순서대로 이어 놨어요. 처음이면 01부터 봐요. 챕터를 누르면 슬라이드와 학습 목표가 나와요.
      </p>

      <div className="news-head">
        <h2>새 소식</h2>
        <Link href="/updates/">
          전체 보기 <ArrowRight className="i" />
        </Link>
      </div>
      <div className="news-strip">
        {news()
          .slice(0, 3)
          .map((n) => (
            <NewsCard key={n.href} item={n} />
          ))}
      </div>

      <h2 className="curr-sub">
        커리큘럼<span>다섯 단계로 이어져요. 단계 안에서도 번호 순서대로 봐요</span>
      </h2>
      <nav className="road" aria-label="단계">
        {stages.map((s) => (
          <a className="road-step" href={`#stage-${s.no}`} key={s.no}>
            <span className="k">{s.no}단계</span>
            <b>{s.title}</b>
            <small>
              {s.from}–{s.to} · {s.count}챕터
            </small>
          </a>
        ))}
      </nav>
      <CurriculumList stages={stages} filters={filters} fresh={fresh} />

      <h2 className="curr-sub" id="extras">
        번외<span>순서와 상관없이 막혔을 때 봐요</span>
      </h2>
      <div className="ch-list">
        {extras.map((e) => (
          <Link className="ch-row extra-row" key={e.dir} href={`/extras/${e.dir}/`}>
            <span className="no" style={{ color: "var(--muted)" }}>
              +
            </span>
            <div>
              <div className="t">{e.title}</div>
              <div className="g" dangerouslySetInnerHTML={{ __html: renderInline(e.summary) }} />
            </div>
            <span className="meta">
              {e.relatedChapters.map((r) => (
                <span className="prereq" key={r.dir}>
                  <b>{r.no}</b>
                </span>
              ))}
            </span>
          </Link>
        ))}
      </div>
    </AppShell>
  );
}
