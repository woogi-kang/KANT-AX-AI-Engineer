import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, ExternalLink } from "lucide-react";
import { roadmap, readRm, ghBlob, sections, strip } from "@/lib/roadmap";
import { Crumb, Ic, Ict, PageHead } from "@/components/ui";
import LibTiles from "@/components/LibTiles";
import CopyText from "@/components/CopyText";
import "../library.css";

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
          <div className="tiles t2">
            {r.templates
              .filter((t) => t.when === w)
              .map((t) => {
                const md = readRm(t.path);
                const n = sections(md).length;
                return (
                  <div key={t.slug} className="tile lb-tpl">
                    <Link className="lb-tpl-h" href={`/library/templates/${t.slug}/`}>
                      <Ict n="file-text" />
                      <span className="lb-tpl-t">
                        <b>{t.t}</b>
                        <small>{n}개 항목</small>
                      </span>
                      <ArrowRight className="i lb-go" aria-hidden="true" />
                    </Link>
                    {purpose(md) && <p className="lb-pur">{purpose(md)}</p>}
                    <div className="acts">
                      <Link className="btn" href={`/library/templates/${t.slug}/`}>
                        양식 보기
                      </Link>
                      <CopyText text={md} label="마크다운 복사" />
                      <a className="btn" href={ghBlob(t.path)} target="_blank" rel="noopener">
                        원문
                        <ExternalLink aria-hidden="true" />
                      </a>
                    </div>
                  </div>
                );
              })}
          </div>
        </section>
      ))}
      <section className="sec">
        <Link className="use" href="/library/failures/#capstone">
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
