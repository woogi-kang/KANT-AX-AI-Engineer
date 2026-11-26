// 챕터와 꿀팁 화면의 "교안" 절이에요. README를 h2 절마다 접는 칸으로 보여 줘요.
import { ChevronDown } from "lucide-react";
import { renderReadme } from "@/lib/markdown";
import { splitSections } from "@/lib/chapter";
import { rehypeLesson } from "@/lib/lesson";
import { SecHead } from "@/components/ui";
import LessonTools from "@/components/LessonTools";
import "./lesson.css";

/** 교안 HTML을 절로 나눠 돌려줘요. skip에 맞는 절(학습 목표, 구성, 강사용 등)은 빼요 */
export async function lessonSections(relDir: string, skip: RegExp) {
  const { html } = await renderReadme(relDir, { dropTitle: true, plugins: [rehypeLesson] });
  return splitSections(html).filter((s) => !skip.test(s.title));
}

/** 접힌 칸 오른쪽에 보이는 개수(명령 27개, 오류 14가지, 4단계) */
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

export default function Lesson({ secs }: { secs: { id: string; title: string; html: string }[] }) {
  return (
    <section className="sec doc lesson">
      <SecHead title="교안" />
      {secs.map((s) => {
        const c = count(s.html, s.title);
        return (
          <details key={s.id} id={s.id}>
            <summary>
              <span className="lt">{s.title}</span>
              {c && <span className="lc-n">{c}</span>}
              <ChevronDown aria-hidden="true" />
            </summary>
            <div className="in prose" dangerouslySetInnerHTML={{ __html: s.html }} />
          </details>
        );
      })}
      <LessonTools />
    </section>
  );
}
