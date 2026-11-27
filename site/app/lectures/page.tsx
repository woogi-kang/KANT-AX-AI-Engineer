import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { load, LEVELS, TRACKS, type LevelName, type TrackName } from "@/lib/content";
import { logosOf, chapterLogo } from "@/lib/logos";
import { Crumb, Cover, extraCoverSrc, Ict, Logo, Logos, PageHead } from "@/components/ui";
import LecCard from "@/components/LecCard";
import LectureFilter from "./LectureFilter";
import "./lectures.css";

export const metadata: Metadata = { title: "강의", description: "터미널, Git, 파이썬, Docker, 데이터베이스까지 배우는 순서대로 모은 기초 강의예요." };

export default function LecturesPage() {
  const { stages, chapters, extras } = load();
  const tracks = (Object.keys(TRACKS) as TrackName[]).map((t) => {
    // "00"은 챕터별 로고가 없어서 분류 대표 로고가 나와요
    return { value: TRACKS[t], label: t, icon: <Logo k={chapterLogo("00", t)} size={18} />, count: chapters.filter((c) => c.track === t).length };
  });
  const levels = (Object.keys(LEVELS) as LevelName[]).map((l) => ({ value: String(LEVELS[l]), label: l, count: chapters.filter((c) => c.level === l).length }));
  return (
    <>
      <Crumb items={[["홈", "/"], ["강의"]]} />
      <PageHead icon={<Ict n="presentation" size="lg" />} title="기초 강의" lede={`배우는 순서대로 ${chapters.length}챕터예요. 표지를 누르면 슬라이드와 PDF가 있어요.`} />
      <LectureFilter tracks={tracks} levels={levels} total={chapters.length} />
      <div id="lec-list">
        {stages.map((s) => {
          const list = chapters.filter((c) => c.stageNo === s.no);
          return (
            <section key={s.no} className="stage" id={`stage-${s.no}`} data-stage={s.no}>
              <div className="th">
                <Logos ks={logosOf(list).slice(0, 3)} size={32} />
                <div>
                  <span className="eyebrow" data-cnt={`${s.no}단계 · ${s.range} · ${list.length}챕터`}>
                    {s.no}단계 · {s.range} · {list.length}챕터
                  </span>
                  <h2>{s.title}</h2>
                </div>
              </div>
              <p className="ss">{s.summary}</p>
              <div className="tiles t4" style={{ marginTop: 16 }}>
                {list.map((c) => (
                  <div key={c.dir} data-track={c.trackKey} data-level={LEVELS[c.level]}>
                    <LecCard c={c} sub={`${c.groupTitle} · ${c.level}`} />
                  </div>
                ))}
              </div>
            </section>
          );
        })}
      </div>
      <section className="stage" id="tips">
        <div className="sh">
          <h2>꿀팁</h2>
          <Link href="/tips/">
            모두 보기
            <ArrowRight aria-hidden="true" />
          </Link>
        </div>
        <p className="ss" style={{ marginTop: -8, marginBottom: 16 }}>
          배우는 순서와 상관없이 막혔을 때 펴 보는 자료예요.
        </p>
        <div className="tiles t4">
          {extras.map((e) => (
            <Link key={e.dir} className="lc" href={`/extras/${e.dir}/`}>
              <Cover src={extraCoverSrc(e.dir)} />
              <div className="bd">
                <b>{e.title}</b>
                <small>관련 챕터 {e.relatedChapters.map((c) => `${c.no} ${c.title}`).join(", ")}</small>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </>
  );
}
