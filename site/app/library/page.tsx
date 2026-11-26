import type { Metadata } from "next";
import Link from "next/link";
import { Play } from "lucide-react";
import { roadmap } from "@/lib/roadmap";
import { caseIcon } from "@/lib/site";
import { Crumb, Diff, Ic, Ict, PageHead } from "@/components/ui";
import LibTiles from "@/components/LibTiles";
import FilterChips from "@/components/FilterChips";

export const metadata: Metadata = { title: "업무 사례" };

export default function LibraryPage() {
  const r = roadmap();
  const areas = [...new Set(r.cases.map((c) => c.area))];
  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["업무 사례"]]} />
      <PageHead icon={<Ict n="briefcase" size="lg" />} title="업무 사례" lede="업무 하나를 처음부터 끝까지 설계해 본 사례예요. 실제 회사의 성과가 아니라 연습용 설계예요." />
      <LibTiles on="cases" />
      <FilterChips
        target="#case-list"
        label="업무 분야"
        param="area"
        options={areas.map((a) => ({ value: a, label: a, icon: <Ic n={caseIcon(a)} />, count: r.cases.filter((c) => c.area === a).length }))}
      />
      <div className="tiles t3" id="case-list">
        {r.cases.map((c) => (
          <Link key={c.id} className="case" href={`/library/cases/${c.id}/`} data-f={c.area}>
            <span className="hd">
              <Ict n={caseIcon(c.area)} tone="n" />
              {c.runnable && (
                <span className="run">
                  <Play aria-hidden="true" />
                  실행 예제
                </span>
              )}
            </span>
            <b>{c.t}</b>
            <span className="ft2">
              <span>{c.area}</span>
              <Diff v={c.diff} />
            </span>
          </Link>
        ))}
      </div>
    </>
  );
}
