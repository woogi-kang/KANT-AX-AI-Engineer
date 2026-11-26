// 챕터 화면의 "확인 문제" 자리예요. 확인 문제 영역이 이 파일(과 components/quiz/ 폴더)을 채워요.
// 챕터 화면(app/chapters/[dir]/page.tsx)은 "바로 쳐 보기" 다음, 교안 절 위에서 <ChapterQuiz dir no parts /> 를 불러요.
// 문제가 없는 챕터는 null을 돌려줘요. 틀리면 window.dispatchEvent(new CustomEvent("deck-go", { detail: 쪽 }))로 그 쪽을 열어요.
// 데이터는 챕터 폴더의 quiz.json이에요.
import type { Part } from "@/lib/chapter";

export default function ChapterQuiz({ dir, no, parts }: { dir: string; no: string; parts: Part[] }) {
  void dir;
  void no;
  void parts;
  return null;
}
