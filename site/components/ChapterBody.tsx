import Link from "next/link";
import { ArrowLeft, ArrowRight } from "lucide-react";
import type { ChapterRef, SlideInfo } from "@/lib/content";
import SiteFooter from "./SiteFooter";

/** 플레이어 아래: 조작 안내, README 본문, 발표자 노트, 이전과 다음 챕터. */
export default function ChapterBody({
  html,
  slides,
  prev,
  next,
  prevLabel = "이전 챕터",
  nextLabel = "다음 챕터",
}: {
  html: string;
  slides: SlideInfo[];
  prev?: ChapterRef | null;
  next?: ChapterRef | null;
  prevLabel?: string;
  nextLabel?: string;
}) {
  const withNotes = slides.filter((s) => s.note);
  return (
    <>
      <p className="slide-hint">
        방향키, <span className="kbd">Space</span>로 애니메이션을 하나씩 봐요. 슬라이드를 한 번 누른 뒤 키를 쳐요. <span className="kbd">F</span> 전체 화면,{" "}
        <span className="kbd">?</span> 단축키 안내예요.
      </p>
      <article className="prose" dangerouslySetInnerHTML={{ __html: html }} />
      {withNotes.length > 0 && (
        <details className="notes">
          <summary>
            장마다 발표자 노트<small>{withNotes.length}장</small>
          </summary>
          <ol>
            {withNotes.map((s) => (
              <li key={s.n}>
                <span className="s">{s.n}</span>
                <div>
                  <b>{s.title}</b>
                  <p>{s.note}</p>
                </div>
              </li>
            ))}
          </ol>
        </details>
      )}
      {(prev || next) && (
        <nav className="pager" aria-label="챕터 이동">
          {prev && (
            <Link href={`/chapters/${prev.dir}/`}>
              <small>
                <ArrowLeft className="i" style={{ width: 12, height: 12, verticalAlign: -1 }} /> {prevLabel}
              </small>
              <b>
                {prev.no} · {prev.title}
              </b>
            </Link>
          )}
          {next && (
            <Link className="next" href={`/chapters/${next.dir}/`}>
              <small>
                {nextLabel} <ArrowRight className="i" style={{ width: 12, height: 12, verticalAlign: -1 }} />
              </small>
              <b>
                {next.no} · {next.title}
              </b>
            </Link>
          )}
        </nav>
      )}
      <SiteFooter />
    </>
  );
}
