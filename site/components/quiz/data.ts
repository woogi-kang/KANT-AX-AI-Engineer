// 챕터 폴더의 quiz.json을 읽어요. 형식은 site/README.md "확인 문제" 절을 봐요.
import fs from "node:fs";
import path from "node:path";
import { ROOT } from "@/lib/content";

export type QuizQ = {
  id: string;
  q: string; // 묻는 글. `코드`는 코드 글꼴로 보여요
  code?: string; // 문제에 붙는 코드나 명령(여러 줄)
  choices: string[]; // 2~4개
  answer: number; // 정답 번호(0부터)
  explain: string; // 해설. 교안과 실제 출력에만 근거해요
  page: number; // 다시 볼 슬라이드 쪽
  verify?: "py"; // "py": check-quiz가 code를 파이썬으로 실행해서 출력이 정답과 같은지 봐요
};
export type QuizPart = { part: string; questions: QuizQ[] };
export type Quiz = { parts: QuizPart[] };

export function loadQuiz(dir: string): Quiz | null {
  const f = path.join(ROOT, dir, "quiz.json");
  if (!fs.existsSync(f)) return null;
  return JSON.parse(fs.readFileSync(f, "utf8")) as Quiz;
}
