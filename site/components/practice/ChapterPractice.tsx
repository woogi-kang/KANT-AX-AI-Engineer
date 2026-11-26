// 챕터 화면의 "바로 쳐 보기" 자리예요. 코드 실행 영역이 이 파일(과 components/practice/ 폴더)을 채워요.
// 챕터 화면(app/chapters/[dir]/page.tsx)은 교안 절 바로 위에서 <ChapterPractice dir no /> 를 불러요.
// 실습이 없는 챕터는 null을 돌려줘서 화면에 아무것도 나오지 않아요.
// 데이터는 챕터 폴더의 practice.json (개발 계획에서 정한 형식)이에요.
export default function ChapterPractice({ dir, no }: { dir: string; no: string }) {
  void dir;
  void no;
  return null;
}
