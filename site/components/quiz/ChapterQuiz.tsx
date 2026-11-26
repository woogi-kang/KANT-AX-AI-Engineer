// 챕터 화면의 "확인 문제" 자리예요. 챕터 화면(app/chapters/[dir]/page.tsx)이 "바로 쳐 보기" 다음, 교안 절 위에서 불러요.
// 데이터는 챕터 폴더의 quiz.json이에요. 문제가 없는 챕터는 null을 돌려줘요.
// 틀리면 "다시 보기" 버튼이 window.dispatchEvent(new CustomEvent("deck-go", { detail: 쪽 }))로 위 슬라이드를 그 쪽으로 열어요.
import type { Part } from "@/lib/chapter";
import { renderInline } from "@/lib/inline";
import { SecHead } from "@/components/ui";
import { loadQuiz } from "./data";
import QuizBox, { type ViewPart } from "./QuizBox";
import "./quiz.css";

export default function ChapterQuiz({ dir, no, parts }: { dir: string; no: string; parts: Part[] }) {
  const quiz = loadQuiz(dir);
  if (!quiz) return null;
  const view: ViewPart[] = quiz.parts
    .filter((p) => p.questions.length)
    .map((p) => {
      const meta = parts.find((x) => x.name === p.part);
      return {
        name: p.part,
        range: meta ? (meta.to > meta.from ? `${meta.from}–${meta.to}쪽` : `${meta.from}쪽`) : "",
        questions: p.questions.map((q) => ({
          id: q.id,
          q: renderInline(q.q),
          code: q.code,
          choices: q.choices.map(renderInline),
          answer: q.answer,
          explain: renderInline(q.explain),
          page: q.page,
        })),
      };
    });
  const total = view.reduce((a, p) => a + p.questions.length, 0);
  if (!total) return null;
  return (
    <section className="sec quiz" id="quiz" aria-labelledby="quiz-h">
      <SecHead title={<span id="quiz-h">확인 문제</span>} right={<span className="cnt">{total}문제</span>} />
      <p className="quiz-lede">파트를 다 보면 풀어 보세요. 틀리면 그 내용이 있는 쪽으로 바로 넘어가요.</p>
      <QuizBox parts={view} no={no} />
    </section>
  );
}
