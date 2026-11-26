import type { Metadata } from "next";
import Link from "next/link";
import { load } from "@/lib/content";
import { logosOf } from "@/lib/logos";
import { Crumb, Ict, Logos, PageHead } from "@/components/ui";
import LecCard from "@/components/LecCard";

export const metadata: Metadata = { title: "강의" };

export default function LecturesPage() {
  const { stages, chapters, extras } = load();
  return (
    <>
      <Crumb items={[["홈", "/"], ["강의"]]} />
      <PageHead icon={<Ict n="presentation" size="lg" />} title="기초 강의" lede={`배우는 순서대로 ${chapters.length}챕터예요. 표지를 누르면 슬라이드와 PDF가 있어요.`} />
      {stages.map((s) => {
        const list = chapters.filter((c) => c.stageNo === s.no);
        return (
          <section key={s.no} className="stage" id={`stage-${s.no}`}>
            <div className="th">
              <Logos ks={logosOf(list).slice(0, 3)} size={32} />
              <div>
                <span className="eyebrow">
                  {s.no}단계 · {s.from}–{s.to} · {list.length}챕터
                </span>
                <h2>{s.title}</h2>
              </div>
            </div>
            <div className="tiles t4" style={{ marginTop: 16 }}>
              {list.map((c) => (
                <LecCard key={c.dir} c={c} sub={`${c.level} · ${c.groupTitle}`} />
              ))}
            </div>
          </section>
        );
      })}
      <section className="stage" id="tips">
        <div className="sh">
          <h2>꿀팁</h2>
          <Link href="/tips/">모두 보기</Link>
        </div>
        <div className="tiles t4">
          {extras.map((e) => (
            <Link key={e.dir} className="tile" href={`/extras/${e.dir}/`}>
              <Ict n="lightbulb" />
              <b>{e.title}</b>
            </Link>
          ))}
        </div>
      </section>
    </>
  );
}
