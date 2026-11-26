import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Download, Presentation, SquareTerminal, TriangleExclamationPoint, CircleCheck, ChevronDown } from "lucide-react";
import { deckUrl, getChapter, load, pdfUrl } from "@/lib/content";
import { renderReadme } from "@/lib/markdown";
import { chapterInfo, splitSections } from "@/lib/chapter";
import { chapterTopics } from "@/lib/links";
import { topicBySlug } from "@/lib/roadmap";
import { chapterLogos } from "@/lib/logos";
import { renderInline, plainInline } from "@/lib/inline";
import { AREA_IC, shortTitle } from "@/lib/site";
import { Cover, coverSrc, Crumb, Ict, Logo, More, SecHead } from "@/components/ui";
import Player from "@/components/Player";
import PartGo from "@/components/PartGo";
import ChapterPractice from "@/components/practice/ChapterPractice";
import ChapterQuiz from "@/components/quiz/ChapterQuiz";

type Params = { params: Promise<{ dir: string }> };
export const dynamicParams = false;
export function generateStaticParams() {
  return load().chapters.map((c) => ({ dir: c.dir }));
}
export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const c = getChapter((await params).dir);
  return { title: `${c.no} ${c.title}`, description: plainInline(c.goal) };
}

// 첫 판: 표지 플레이어, 파트(누르면 그 쪽으로), 학습 목표, README 절. 강의 영역에서 파트 그림, 실습 칸으로 다듬어요.
export default async function ChapterPage({ params }: Params) {
  const c = getChapter((await params).dir);
  const { goals, parts } = chapterInfo(c.dir);
  const { html } = await renderReadme(c.dir);
  const secs = splitSections(html).filter((s) => !/^(학습 목표|구성|강사용)/.test(s.title));
  const topics = chapterTopics(c.no).map(topicBySlug);
  const deck = deckUrl(c.dir, c.slides);
  const logos = chapterLogos(c.no, c.track);
  const secId = (re: RegExp) => secs.find((s) => re.test(s.title))?.id;
  const cmd = secId(/^명령어 요약/);
  const fix = secId(/^문제 해결/);
  return (
    <>
      <Crumb items={[["강의", "/lectures/"], [`${c.stageNo}. ${c.stageTitle}`, `/lectures/#stage-${c.stageNo}`], [c.no]]} />
      <div className="th">
        <Logo k={logos[0]} size={56} />
        <div>
          <span className="eyebrow">
            {c.no} · {c.track} · {c.level}
          </span>
          <h1>{shortTitle(c.title)}</h1>
        </div>
      </div>
      <p className="lede" dangerouslySetInnerHTML={{ __html: renderInline(c.goal) }} />
      <Player src={deck} cover={coverSrc(c.no)} title={c.title} />
      <div className="acts">
        <a href={deck} target="_blank" rel="noopener">
          <Presentation aria-hidden="true" />
          크게 보기
        </a>
        <a href={pdfUrl(c.dir, c.slides)} target="_blank" rel="noopener">
          <Download aria-hidden="true" />
          PDF 받기
        </a>
        {cmd && (
          <a href={`#${cmd}`}>
            <SquareTerminal aria-hidden="true" />
            명령어 요약
          </a>
        )}
        {fix && (
          <a href={`#${fix}`}>
            <TriangleExclamationPoint aria-hidden="true" />
            문제 해결
          </a>
        )}
      </div>

      {parts.length > 0 && (
        <section className="sec">
          <SecHead title="구성" right={<span className="cnt">파트 {parts.length}개</span>} />
          <div className="tiles t4">
            {parts.map((p) => (
              <PartGo key={p.from} page={p.from} className="part">
                <span className="pt">
                  <b>{p.name}</b>
                  <small>
                    {p.from}
                    {p.to > p.from ? `–${p.to}` : ""}
                  </small>
                </span>
              </PartGo>
            ))}
          </div>
          {goals.length > 0 && (
            <More label={`배우는 것 ${goals.length}가지`}>
              <ul className="goals">
                {goals.map((g) => (
                  <li key={g}>
                    <CircleCheck aria-hidden="true" />
                    <span dangerouslySetInnerHTML={{ __html: renderInline(g) }} />
                  </li>
                ))}
              </ul>
            </More>
          )}
        </section>
      )}

      {topics.length > 0 && (
        <section className="sec">
          {topics.map((t) => (
            <Link key={t.slug} className="use" href={`/roadmap/${t.slug}/`} style={{ marginTop: 10 }}>
              <Ict n={AREA_IC[t.slug] ?? "route"} size="lg" />
              <span>
                <small>이 챕터를 쓰는 로드맵 주제</small>
                <b>
                  {t.stage}단계 · {t.t}
                </b>
              </span>
              <span className="go">
                <ArrowRight aria-hidden="true" />
              </span>
            </Link>
          ))}
        </section>
      )}

      {/* 코드 실행 영역 자리: 실습 칸(바로 쳐 보기). 내용은 components/practice/ 에서 채워요 */}
      <ChapterPractice dir={c.dir} no={c.no} />
      {/* 확인 문제 영역 자리: 파트별 문제. 내용은 components/quiz/ 에서 채워요 */}
      <ChapterQuiz dir={c.dir} no={c.no} parts={parts} />

      <section className="sec doc">
        <SecHead title="교안" />
        {secs.map((s) => (
          <details key={s.id} id={s.id}>
            <summary>
              {s.title}
              <ChevronDown aria-hidden="true" />
            </summary>
            <div className="in prose" dangerouslySetInnerHTML={{ __html: s.html }} />
          </details>
        ))}
      </section>

      <nav className="pn" aria-label="이전, 다음 챕터">
        {c.prev ? (
          <Link href={`/chapters/${c.prev.dir}/`}>
            <Cover src={coverSrc(c.prev.no)} />
            <span>
              <small>이전</small>
              <b>
                {c.prev.no} {shortTitle(c.prev.title)}
              </b>
            </span>
          </Link>
        ) : (
          <span className="empty" />
        )}
        {c.next ? (
          <Link className="r" href={`/chapters/${c.next.dir}/`}>
            <Cover src={coverSrc(c.next.no)} />
            <span>
              <small>다음</small>
              <b>
                {c.next.no} {shortTitle(c.next.title)}
              </b>
            </span>
          </Link>
        ) : (
          <span className="empty" />
        )}
      </nav>
    </>
  );
}
