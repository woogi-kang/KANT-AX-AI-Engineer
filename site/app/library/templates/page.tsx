import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { roadmap, readRm, sections, strip } from "@/lib/roadmap";
import { Crumb, Ic, Ict, PageHead } from "@/components/ui";
import LibTiles from "@/components/LibTiles";
import "../library.css";

/** 양식마다 하는 일을 보여 주는 아이콘 */
const TPL_ICON: Record<string, string> = {
  "workflow-discovery-card": "search",
  "use-case-scorecard": "gauge",
  "execution-contract": "signature",
  "experiment-card": "flask-conical",
  "evidence-ledger": "notebook-pen",
  "case-study-template": "book-open",
  "reusable-skill-card": "repeat",
  "ui-integration-checklist": "monitor-check",
};

export const metadata: Metadata = { title: "실무 템플릿" };

/** 양식 첫 문단(무엇을 정리하는 양식인지) */
/** 첫 "## " 앞의 첫 문단. 없으면 빈칸 */
const purpose = (md: string) => strip(md.replace(/^# .+\n+/m, "").split(/\n(?=## )/)[0].split("\n\n").find((b) => b.trim() && !/^[#|>-]/.test(b.trim())) ?? "");

export default function TemplatesPage() {
  const r = roadmap();
  const whens = [...new Set(r.templates.map((t) => t.when))];
  return (
    <>
      <Crumb items={[["사례와 자료", "/library/"], ["실무 템플릿"]]} />
      <PageHead icon={<Ict n="clipboard-check" size="lg" />} title="실무 템플릿" lede="업무를 바꿀 때 빠뜨리기 쉬운 판단과 책임을 확인하는 양식이에요. 업무 위험과 규모에 맞게 줄여 써요." />
      <LibTiles on="templates" />
      {whens.map((w, k) => (
        <section key={w} className="sec lb-when">
          <div className="lb-when-h">
            <span className="lb-qn">{k + 1}</span>
            <h2>{w}</h2>
          </div>
          <div className="lb-tpls">
            {r.templates
              .filter((t) => t.when === w)
              .map((t) => {
                const md = readRm(t.path);
                const n = sections(md).length;
                return (
                  <Link key={t.slug} className="lb-tplc" href={`/library/templates/${t.slug}/`}>
                    <span className="lb-tplc-i">
                      <Ic n={TPL_ICON[t.slug] ?? "file-text"} />
                    </span>
                    <span className="lb-org-b">
                      <b>{t.t}</b>
                      {purpose(md) && <span className="lb-org-w">{purpose(md)}</span>}
                      <span className="lb-org-m">{n}개 항목</span>
                    </span>
                    <ArrowRight className="i lb-go" aria-hidden="true" />
                  </Link>
                );
              })}
          </div>
        </section>
      ))}
      <section className="sec">
        <Link className="use" href="/library/failures/#캡스톤-설계에-쓰는-점검표">
          <Ict n="list-checks" />
          <span>
            <b>캡스톤 설계 점검표</b>
            <small>공개 실패·중단 사례에서 뽑은 여덟 질문이에요. 답은 업무 실행 규칙과 실험 카드에 옮겨요.</small>
          </span>
          <Ic n="arrow-right" className="i go" />
        </Link>
      </section>
    </>
  );
}
