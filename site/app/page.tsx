import Link from "next/link";
import { ArrowRight, LifeBuoy, Megaphone, Sparkles } from "lucide-react";
import AppShell from "@/components/AppShell";
import CurriculumList from "@/components/CurriculumList";
import LogoTile from "@/components/LogoTile";
import { TRACKS, isNew, load, news, type TrackKey } from "@/lib/content";
import { LOGOS, chapterLogos, stageLogos, type Logo, type LogoKey } from "@/lib/logos";
import { plainInline } from "@/lib/inline";

const TRACK_LOGO: Record<TrackKey, LogoKey> = { term: "terminal", git: "git", gh: "github", py: "python", docker: "docker", db: "postgresql" };
const CLOUD: LogoKey[] = ["terminal", "git", "github", "uv", "jupyter", "python", "docker", "nginx", "mysql", "postgresql", "numpy", "pandas"];

export default function Home() {
  const { stages, chapters, extras } = load();
  const filters = [
    { key: "all" as const, label: "전체", count: chapters.length },
    ...Object.entries(TRACKS).map(([label, key]) => ({
      key,
      label,
      count: chapters.filter((c) => c.trackKey === key).length,
      logo: LOGOS[TRACK_LOGO[key]] as Logo,
    })),
  ];
  const logos: Record<string, Logo[]> = Object.fromEntries(chapters.map((c) => [c.dir, chapterLogos(c.no, c.track).map((k) => LOGOS[k] as Logo)]));
  const fresh = chapters.filter((c) => isNew(c)).map((c) => c.dir);
  const latest = news().slice(0, 3);
  return (
    <AppShell current="home">
      <section className="hero">
        <div className="hero-t">
          <span className="eyebrow">
            <Sparkles className="i" />
            무료 학습 로드맵
          </span>
          <h1>
            터미널부터 데이터 분석까지
            <br />
            배우는 순서대로 한 길로
          </h1>
          <p>개발이 처음이어도 따라올 수 있게, 애니메이션 슬라이드와 실제로 실행한 화면으로 배워요.</p>
          <div className="hero-cta">
            <Link className="btn primary" href={`/chapters/${chapters[0].dir}/`}>
              01부터 시작하기 <ArrowRight className="i" />
            </Link>
            <a className="btn secondary" href="#roadmap">
              로드맵 보기
            </a>
          </div>
          <dl className="stats">
            <div>
              <dt>챕터</dt>
              <dd>{chapters.length}</dd>
            </div>
            <div>
              <dt>단계</dt>
              <dd>{stages.length}</dd>
            </div>
            <div>
              <dt>도구</dt>
              <dd>{CLOUD.length}</dd>
            </div>
            <div>
              <dt>수강료</dt>
              <dd>0원</dd>
            </div>
          </dl>
        </div>
        <div className="cloud" aria-label="배우는 도구">
          {CLOUD.map((k, i) => (
            <span className="cloud-i" key={k} style={{ animationDelay: `${i * 60}ms` }}>
              <LogoTile logo={LOGOS[k] as Logo} size={52} label />
              <small>{LOGOS[k].title}</small>
            </span>
          ))}
        </div>
      </section>

      <section className="news-bar" aria-label="업데이트">
        <Megaphone className="i" />
        <div className="news-items">
          {latest.map((n) => (
            <Link key={n.href} href={n.href}>
              <span className={`badge ${n.kind === "chapter" ? "run" : "mark"}`}>{n.kind === "chapter" ? "새 챕터" : "업데이트"}</span>
              {n.title}
            </Link>
          ))}
        </div>
        <Link className="more" href="/updates/">
          전체 <ArrowRight className="i" />
        </Link>
      </section>

      <h2 className="sec-h" id="roadmap">
        학습 로드맵<span>다섯 단계를 차례로 밟아요</span>
      </h2>
      <nav className="road" aria-label="단계">
        {stages.map((s) => {
          const ks = stageLogos(s.groups.flatMap((g) => g.chapters)).slice(0, 4);
          return (
            <a className="road-step" href={`#stage-${s.no}`} key={s.no}>
              <span className="k">STEP {s.no}</span>
              <b>{s.title}</b>
              <span className="road-logos">
                {ks.map((k) => (
                  <LogoTile key={k} logo={LOGOS[k] as Logo} size={26} />
                ))}
              </span>
              <small>{s.count}챕터</small>
            </a>
          );
        })}
      </nav>
      <CurriculumList stages={stages} filters={filters} fresh={fresh} logos={logos} />

      <h2 className="sec-h" id="guides">
        가이드<span>순서와 상관없이 막혔을 때 꺼내 봐요</span>
      </h2>
      <div className="guides">
        {extras.map((e) => (
          <Link className="guide" key={e.dir} href={`/extras/${e.dir}/`}>
            <span className="guide-i">
              <LifeBuoy width={26} height={26} />
            </span>
            <div>
              <b>{e.title}</b>
              <p>{plainInline(e.summary).split(", ").slice(0, 2).join(", ")}</p>
              <span className="guide-rel">
                {e.relatedChapters.map((r) => (
                  <span className="prereq" key={r.dir} title={r.title}>
                    <b>{r.no}</b>
                    {r.title.length > 10 ? r.title.slice(0, 10) + "…" : r.title}
                  </span>
                ))}
              </span>
            </div>
          </Link>
        ))}
      </div>
    </AppShell>
  );
}
