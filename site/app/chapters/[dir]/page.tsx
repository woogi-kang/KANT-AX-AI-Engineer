import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Download, Presentation, SquareTerminal, TriangleExclamationPoint, CircleCheck } from "lucide-react";
import { deckUrl, getChapter, load, pdfUrl } from "@/lib/content";
import { chapterInfo } from "@/lib/chapter";
import { chapterTopics } from "@/lib/links";
import { topicBySlug } from "@/lib/roadmap";
import { chapterLogos } from "@/lib/logos";
import { renderInline, plainInline } from "@/lib/inline";
import { AREA_IC, shortTitle } from "@/lib/site";
import { Cover, coverSrc, Crumb, Ict, Logo, More, partSrc, SecHead } from "@/components/ui";
import Player from "@/components/Player";
import PartGo from "@/components/PartGo";
import Lesson, { lessonSections } from "@/components/Lesson";
import "./chapter.css";
import ChapterPractice, { practiceOf } from "@/components/practice/ChapterPractice";
import { loadQuiz } from "@/components/quiz/data";
import StudyTabs, { type StudyTab } from "@/components/StudyTabs";
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

// 표지 플레이어, 파트 카드(파트 첫 장 그림, 누르면 그 쪽으로), 학습 목표, 로드맵 주제, 실습 칸, 확인 문제, 교안, 이전/다음 챕터.
export default async function ChapterPage({ params }: Params) {
  const c = getChapter((await params).dir);
  const { goals, parts } = chapterInfo(c.dir);
  const secs = await lessonSections(c.dir, /^(학습 목표|구성|강사용)/);
  const topics = chapterTopics(c.no).map(topicBySlug);
  const deck = deckUrl(c.dir, c.slides);
  const logos = chapterLogos(c.no, c.track);
  const secId = (re: RegExp) => secs.find((s) => re.test(s.title))?.id;
  const cmd = secId(/^명령어 요약/);
  const fix = secId(/^문제 해결/);
  // 슬라이드 아래 공부 칸 탭: 구성, 바로 쳐 보기(있을 때), 확인 문제(있을 때), 교안
  const pr = practiceOf(c.dir);
  const prN = pr ? pr.cells.filter((x) => !x.hidden).length : 0;
  const qz = loadQuiz(c.dir);
  const qzN = qz ? qz.parts.reduce((a, p) => a + p.questions.length, 0) : 0;
  const tabs: StudyTab[] = [
    { id: "overview", label: "구성", count: parts.length ? `${parts.length}` : undefined },
    ...(prN ? [{ id: "practice", label: "바로 쳐 보기", count: `${prN}` }] : []),
    ...(qzN ? [{ id: "quiz", label: "확인 문제", count: `${qzN}` }] : []),
    ...(secs.length ? [{ id: "lesson", label: "교안" }] : []),
  ];
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

      <StudyTabs tabs={tabs}>
      <div data-panel="overview" id="panel-overview" role="tabpanel" aria-labelledby="tab-overview">
      {parts.length > 0 && (
        <section className="sec">
          <p className="study-lead">파트를 누르면 위 슬라이드가 그 쪽에서 열려요.</p>
          <div className="tiles t4 parts-grid">
            {parts.map((p) => (
              <PartGo key={p.from} page={p.from} className="part" label={`${p.name}, ${p.from}쪽부터 슬라이드 보기`}>
                <Cover src={partSrc(c.dir, p.from)} />
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

      </div>
      {/* 코드 실행 영역 자리: 실습 칸(바로 쳐 보기). 내용은 components/practice/ 에서 채워요 */}
      {prN > 0 && (
        <div data-panel="practice" id="panel-practice" role="tabpanel" aria-labelledby="tab-practice">
          <ChapterPractice dir={c.dir} no={c.no} />
        </div>
      )}
      {/* 확인 문제 영역 자리: 파트별 문제. 내용은 components/quiz/ 에서 채워요 */}
      {qzN > 0 && (
        <div data-panel="quiz" id="panel-quiz" role="tabpanel" aria-labelledby="tab-quiz">
          <ChapterQuiz dir={c.dir} no={c.no} parts={parts} />
        </div>
      )}
      {secs.length > 0 && (
        <div data-panel="lesson" id="panel-lesson" role="tabpanel" aria-labelledby="tab-lesson">
          <Lesson secs={secs} />
        </div>
      )}
      </StudyTabs>

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
