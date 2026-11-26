// 챕터 화면의 "바로 쳐 보기" 자리예요. 챕터 폴더의 practice.json을 읽어 실습 칸을 그려요.
// 챕터 화면(app/chapters/[dir]/page.tsx)은 교안 절 바로 위에서 <ChapterPractice dir no /> 를 불러요.
// 실습이 없는 챕터는 null을 돌려줘서 화면에 아무것도 나오지 않아요.
// practice.json 형식과 만드는 법은 site/scripts/practice/README.md에 있어요.
import fs from "node:fs";
import path from "node:path";
import { ROOT } from "@/lib/content";
import { SecHead } from "@/components/ui";
import PracticeBox, { type PartView } from "./PracticeBox";
import "./practice.css";

type Cell = {
  id: string;
  code?: string;
  expect?: string[];
  page?: number;
  title?: string;
  part?: string;
  hidden?: boolean;
  diff?: string;
  err?: boolean;
  cut?: number;
  steps?: { cmd: string; out: string[]; cwd?: string; note?: string }[];
};
type Data = { kind: "python" | "sql" | "replay"; cells: Cell[]; prompt?: string; source?: string };

const MAX = 400; // 화면에 넣는 수업 출력 줄 수
const SIZE = { python: "13MB", sql: "16MB", replay: "" };
const LEAD = {
  python: "코드를 고쳐서 바로 실행해 봐요. 브라우저 안에서 파이썬 3.14가 돌아가요.",
  sql: "SQL을 고쳐서 바로 실행해 봐요. 브라우저 안에서 PostgreSQL 19가 돌아가요. 수업(PostgreSQL 18) 화면과 조금 다를 수 있어요.",
  replay: "수업에서 친 명령을 똑같이 쳐 보세요. 맞으면 수업에서 실제로 나온 화면을 보여 줘요.",
};

export function practiceOf(dir: string): Data | null {
  const p = path.join(ROOT, dir, "practice.json");
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

export default function ChapterPractice({ dir, no }: { dir: string; no: string }) {
  void no;
  const data = practiceOf(dir);
  if (!data) return null;
  const parts: PartView[] = [];
  let count = 0;
  for (const c of data.cells) {
    if (c.hidden) continue;
    const name = (c.part || "실습").replace(/^\d+\.\s*/, "");
    let pt = parts.find((p) => p.name === name);
    if (!pt) parts.push((pt = { name, cells: [] }));
    count++;
    if (data.kind === "replay") {
      pt.cells.push({ id: c.id, page: c.page, title: c.title, steps: c.steps ?? [], diff: c.diff });
    } else {
      const expect = c.expect ?? [];
      pt.cells.push({
        id: c.id,
        code: c.code ?? "",
        expect: expect.slice(0, MAX),
        cut: c.cut ?? (expect.length > MAX ? expect.length : undefined),
        page: c.page,
        title: c.title,
        diff: c.diff,
        err: c.err,
      });
    }
  }
  if (!count) return null;
  // 데이터 순서(실행 흐름)와 상관없이 화면은 덱 쪽 순서로 보여 줘요.
  const first = (pt: PartView) => Math.min(...pt.cells.map((c) => c.page ?? 9999));
  for (const pt of parts) pt.cells.sort((a, b) => (a.page ?? 9999) - (b.page ?? 9999));
  parts.sort((a, b) => first(a) - first(b));
  return (
    <section className="sec practice" id="practice" aria-labelledby="practice-h">
      <SecHead title={<span id="practice-h">바로 쳐 보기</span>} right={<span className="cnt">실습 칸 {count}개</span>} />
      <p className="pc-lead">{LEAD[data.kind]}</p>
      <PracticeBox dir={dir} kind={data.kind} parts={parts} size={SIZE[data.kind]} />
    </section>
  );
}
