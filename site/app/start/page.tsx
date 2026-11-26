import type { Metadata } from "next";
import { roadmap } from "@/lib/roadmap";
import { START } from "@/lib/home";
import { Crumb, Ict, PageHead } from "@/components/ui";

export const metadata: Metadata = { title: "시작하기" };

// 첫 판: 로드맵 README의 "나에게 맞는 시작점" 표. 로드맵 영역에서 v16 모양(큰 타일, 단계별 길 그림)으로 다듬어요.
export default function StartPage() {
  const r = roadmap();
  const keys = ["new", "dev", "biz", "words", "run"];
  return (
    <>
      <Crumb items={[["홈", "/"], ["시작하기"]]} />
      <PageHead icon={<Ict n="signpost" size="lg" />} title="어디서 시작할까요?" lede="지금 나와 가까운 줄을 골라요. 처음 할 일과 이어서 볼 곳이 있어요." />
      <div className="tiles t2" style={{ marginTop: 24 }}>
        {r.start.map((s, n) => {
          const st = START.find((x) => x.key === keys[n]);
          return (
            <section key={s.who} id={keys[n]} className="tile">
              {st && <Ict n={st.icon} size="lg" />}
              <b>{s.who}</b>
              <small>처음 할 일: {s.first}</small>
              <small>이어서 볼 곳: {s.go}</small>
            </section>
          );
        })}
      </div>
    </>
  );
}
