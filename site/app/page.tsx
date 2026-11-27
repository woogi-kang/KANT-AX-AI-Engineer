import Link from "next/link";
import { ArrowRight, Search } from "lucide-react";
import { load, news } from "@/lib/content";
import { roadmap } from "@/lib/roadmap";
import { logosOf } from "@/lib/logos";
import { STAGE_IC, LIB_IC, LIB_HREF, LIB_NAME, stageShort, type LibKey } from "@/lib/site";
import { libCounts, stageCount, START } from "@/lib/home";
import { Ict, Logos, Cover, coverSrc, More, SecHead } from "@/components/ui";

export default function Home() {
  const { stages, chapters } = load();
  const r = roadmap();
  const counts = libCounts();
  return (
    <>
      <h1>AX 엔지니어 핸드북</h1>
      <p className="lede">AX 엔지니어가 되는 길과 그 길에 필요한 기초 강의를 한곳에 모았어요.</p>
      <button className="search" type="button" data-search>
        <Search aria-hidden="true" />
        <span>트랜잭션, MCP, 법인카드 정산처럼 찾아요</span>
        <kbd>/</kbd>
      </button>
      <More label="AX 엔지니어는 어떤 일을 하나요?">
        <p>{r.defn}</p>
        <p>
          <Link href="/roadmap/" style={{ color: "var(--ac)" }}>
            로드맵에서 자세히 보기
          </Link>
        </p>
      </More>

      <section className="sec" id="start">
        <SecHead title="어디서 시작할까요?" />
        <div className="tiles t6">
          {START.map((s) => (
            <Link key={s.key} className="tile c" href={s.href}>
              <Ict n={s.icon} size="lg" />
              <b>{s.label}</b>
            </Link>
          ))}
        </div>
      </section>

      <section className="sec">
        <SecHead
          title="로드맵 5단계"
          right={
            <Link href="/roadmap/">
              전체 보기 <ArrowRight aria-hidden="true" />
            </Link>
          }
        />
        <div className="tiles t5">
          {r.stages.map((s) => (
            <Link key={s.no} className="tile" href={`/roadmap/#stage-${s.no}`}>
              <span className="no">{s.no}단계</span>
              <Ict n={STAGE_IC[s.no]} size="lg" />
              <b>{stageShort(s.title)}</b>
              <small>{stageCount(s.no)}</small>
            </Link>
          ))}
        </div>
      </section>

      <section className="sec">
        <SecHead
          title="기초 강의"
          right={
            <Link href="/lectures/">
              {chapters.length}챕터 모두 <ArrowRight aria-hidden="true" />
            </Link>
          }
        />
        <div className="tiles t5">
          {stages.map((s) => {
            const list = chapters.filter((c) => c.stageNo === s.no);
            return (
              <Link key={s.no} className="lc" href={`/lectures/#stage-${s.no}`}>
                <Cover src={coverSrc(s.from)} />
                <div className="bd">
                  <Logos ks={logosOf(list).slice(0, 4)} size={26} />
                  <b>{s.title}</b>
                  <small>
                    {s.range} · {list.length}챕터
                  </small>
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      <section className="sec">
        <SecHead title="사례와 자료" />
        <div className="tiles t5">
          {(Object.keys(LIB_IC) as LibKey[]).map((k) => (
            <Link key={k} className="tile" href={LIB_HREF[k]}>
              <Ict n={LIB_IC[k]} />
              <span className="num">{counts[k]}</span>
              <b>{LIB_NAME[k]}</b>
            </Link>
          ))}
        </div>
      </section>

      <section className="sec" id="news">
        <SecHead
          title={<span style={{ fontSize: 18 }}>소식</span>}
          right={
            <Link href="/updates/">
              모두 보기 <ArrowRight aria-hidden="true" />
            </Link>
          }
        />
        <ul className="news">
          {news()
            .slice(0, 3)
            .map((n) => (
              <li key={n.href}>
                <Link href={n.href}>
                  <time dateTime={n.date}>{n.date}</time>
                  <span className={n.kind === "update" ? "badge" : "badge ac"}>{n.kind === "update" ? "업데이트" : "새 챕터"}</span>
                  <span>{n.title}</span>
                </Link>
              </li>
            ))}
        </ul>
      </section>
    </>
  );
}
