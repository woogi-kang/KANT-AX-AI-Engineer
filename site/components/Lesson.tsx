// 챕터와 꿀팁 화면의 "교안"이에요. README를 h2 절로 나눠, 왼쪽(휴대폰은 위) 절 목록에서 고른 절 하나만 크게 보여 줘요.
import { renderReadme } from "@/lib/markdown";
import { splitSections } from "@/lib/chapter";
import { rehypeLesson } from "@/lib/lesson";
import LessonTools from "@/components/LessonTools";
import "./lesson.css";

/** 교안 HTML을 절로 나눠 돌려줘요. skip에 맞는 절(학습 목표, 구성, 강사용 등)은 빼요 */
export async function lessonSections(relDir: string, skip: RegExp) {
  const { html } = await renderReadme(relDir, { dropTitle: true, plugins: [rehypeLesson] });
  return splitSections(html).filter((s) => !skip.test(s.title));
}

/** 절 목록 옆에 보이는 개수(명령 27개, 오류 14가지, 4단계) */
function count(html: string, title: string) {
  const n = (re: RegExp) => (html.match(re) ?? []).length;
  if (/^(명령어 요약|단축키 요약)/.test(title)) {
    const c = n(/class="cmd"/g);
    return c ? `${c}개` : "";
  }
  if (/^문제 해결/.test(title)) {
    const c = n(/class="fix"/g);
    return c ? `${c}가지` : "";
  }
  if (/^실습/.test(title)) {
    const c = n(/class="step"/g);
    return c ? `${c}단계` : "";
  }
  return "";
}
/** 교안의 "실습"은 따라 치는 순서라서, 위 "바로 쳐 보기"와 헷갈리지 않게 목록에서는 이름을 풀어 써요 */
const label = (t: string) => (t === "실습" ? "실습 순서" : t);

export type LessonSec = { id: string; title: string; html: string };

export default function Lesson({ secs }: { secs: LessonSec[] }) {
  if (!secs.length) return null;
  return (
    <div className="lesson lesson-v2" data-sec={secs[0].id}>
      <nav className="ls-toc" aria-label="교안 절">
        {secs.map((s, i) => {
          const c = count(s.html, s.title);
          return (
            <button key={s.id} type="button" data-to={s.id} aria-current={i === 0}>
              <span>{label(s.title)}</span>
              {c && <small>{c}</small>}
            </button>
          );
        })}
      </nav>
      <div className="ls-body">
        {secs.map((s, i) => (
          <section key={s.id} id={s.id} data-sec-id={s.id} className="ls-sec" aria-label={s.title} hidden={i > 0}>
            <h2>{label(s.title)}</h2>
            <div className="prose" dangerouslySetInnerHTML={{ __html: s.html }} />
          </section>
        ))}
      </div>
      <LessonTools />
    </div>
  );
}
