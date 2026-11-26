import type { Metadata } from "next";
import Link from "next/link";
import { Play } from "lucide-react";
import { roadmap, readRmJson, ghBlob } from "@/lib/roadmap";
import { caseIcon } from "@/lib/site";
import { Crumb, Diff, Ic, Ict, More, PageHead } from "@/components/ui";
import LibTiles from "@/components/LibTiles";
import LibFilter from "@/components/LibFilter";
import "./library.css";

export const metadata: Metadata = { title: "업무 사례" };

export default function LibraryPage() {
  const r = roadmap();
  const areas = [...new Set(r.cases.map((c) => c.area))];
  const aKey = (a: string) => `a${areas.indexOf(a)}`;
  const order = new Map(r.cases.map((c) => [c.id, readRmJson<{ learning_order: number }>(`case-studies/${c.id}/case.json`).learning_order]));
  const diffs = [...new Set(r.cases.map((c) => c.diff))].sort();
  const runN = r.cases.filter((c) => c.runnable).length;
  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["업무 사례"]]} />
      <PageHead icon={<Ict n="briefcase" size="lg" />} title="업무 사례" lede="업무 하나를 처음부터 끝까지 설계해 본 사례예요. 실제 회사의 성과가 아니라 연습용 설계예요." />
      <More label="사례를 읽기 전에">
        <p>
          공개한 근거는 재현할 수 있는 공개 시뮬레이션 {runN}개와 실행 전 설계 문서 {r.cases.length - runN}개예요. 지금 공개한 결과는 모두 외부 시스템을 바꾸지 않아요.
        </p>
        <p>목표 실행 범위와 설계 P단계는 앞으로 연습할 최대 범위예요. 구현을 마쳤거나 조직에서 운영한다는 뜻이 아니에요.</p>
        <p>
          카드의 번호는 책임이 커지는 추천 학습 순서예요. 사례의 우열이 아니에요. 원문:{" "}
          <a className="lk" href={ghBlob("case-studies/README.md")}>
            case-studies/README.md
          </a>
        </p>
      </More>
      <LibTiles on="cases" />
      <LibFilter
        target="#case-list"
        unit="개"
        groups={[
          { key: "area", label: "업무 분야", options: areas.map((a) => ({ value: aKey(a), label: a, icon: <Ic n={caseIcon(a)} />, count: r.cases.filter((c) => c.area === a).length })) },
          { key: "diff", label: "난이도", options: diffs.map((d) => ({ value: String(d), label: `${d}단계`, count: r.cases.filter((c) => c.diff === d).length })) },
          { key: "run", label: "실행 예제", options: [{ value: "yes", label: "실행 예제 있음", icon: <Play className="i" aria-hidden="true" />, count: runN }] },
        ]}
      />
      <div className="tiles t3" id="case-list">
        {r.cases.map((c) => (
          <Link key={c.id} className="case" href={`/library/cases/${c.id}/`} data-item="" data-area={aKey(c.area)} data-diff={String(c.diff)} data-run={c.runnable ? "yes" : "no"}>
            <span className="hd">
              <Ict n={caseIcon(c.area)} tone="n" />
              <span className="lb-tags">
                {c.runnable && (
                  <span className="run">
                    <Play aria-hidden="true" />
                    실행 예제
                  </span>
                )}
                <span className="lb-ord" title="추천 학습 순서">
                  {order.get(c.id)}
                </span>
              </span>
            </span>
            <b>{c.t}</b>
            <span className="lb-sub">
              {c.area} · {c.industry}
            </span>
            <span className="ft2">
              <span className="lb-risk">위험 {c.risk}</span>
              <Diff v={c.diff} />
            </span>
          </Link>
        ))}
      </div>
    </>
  );
}
