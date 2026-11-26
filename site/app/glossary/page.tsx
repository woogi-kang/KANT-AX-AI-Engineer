import type { Metadata } from "next";
import fs from "node:fs";
import path from "node:path";
import Link from "next/link";
import { glossary } from "@/lib/search";
import { load } from "@/lib/content";
import { ghBlob, readRm, strip, topicBySlug, ROADMAP_URL } from "@/lib/roadmap";
import { renderMarkdown } from "@/lib/markdown";
import { chapterLogo } from "@/lib/logos";
import { AREA_IC } from "@/lib/site";
import { Crumb, Ic, Ict, Logo, NumBox, PageHead, SecHead } from "@/components/ui";
import GlossaryTools from "./GlossaryTools";
import "./glossary.css";

export const metadata: Metadata = { title: "용어 사전", description: "AX 용어가 업무에서 뜻하는 것과 꼭 물을 질문, 이어서 볼 로드맵 주제와 강의예요." };

type GLinks = { terms: Record<string, { topics?: string[]; chapters?: string[] }>; codes: Record<string, { href?: string; repo?: string }> };
const SRC = "start-here/non-developer-glossary.md";
const isKo = (s: string) => /^[가-힣]/.test(s);

export default async function GlossaryPage() {
  const gl = JSON.parse(fs.readFileSync(path.join(process.cwd(), "content", "glossary-links.json"), "utf8")) as GLinks;
  const byNo = new Map(load().chapters.map((c) => [c.no, c]));
  const inline = async (s: string) => (await renderMarkdown(s)).replace(/^<p>|<\/p>\n?$/g, "");
  const raw = glossary();
  for (const k of Object.keys(gl.terms)) if (!raw.some((g) => g.term === k)) throw new Error(`glossary-links.json: 용어 안내에 없는 용어 ${k}`);
  const rows = (
    await Promise.all(
      raw.map(async (x) => ({
        ...x,
        plain: strip(x.term),
        g: isKo(strip(x.term)) ? "ko" : "en",
        termH: await inline(x.term),
        meanH: await inline(x.mean),
        askH: await inline(x.ask),
        q: strip(`${x.term} ${x.mean} ${x.ask}`).replace(/`/g, ""),
        link: gl.terms[x.term] ?? {},
      })),
    )
  ).sort((a, b) => (a.g === b.g ? a.plain.localeCompare(b.plain, a.g === "ko" ? "ko" : "en") : a.g === "ko" ? -1 : 1));
  const counts = { all: rows.length, ko: rows.filter((r) => r.g === "ko").length, en: rows.filter((r) => r.g === "en").length };

  /* 로드맵 코드 한눈에 보기 */
  const md = readRm(SRC);
  const codeBlock = md.split("## 로드맵 코드 한눈에 보기")[1]?.split("\n## ")[0] ?? "";
  const codeRows = codeBlock
    .split("\n")
    .filter((l) => /^\|/.test(l) && !/^\|[\s|:-]+\|$/.test(l))
    .slice(1)
    .map((l) => l.slice(1, -1).split(" | ").map((c) => c.trim().replace(/^\|\s*/, "")));
  const codeNote = strip(codeBlock.split("\n\n").map((p) => p.trim()).filter((p) => p && !p.startsWith("|")).join(" "));
  const codes = await Promise.all(
    codeRows.map(async ([c, mean, ask]) => {
      const key = c.replace(/`/g, "");
      const l = gl.codes[key];
      const href = l?.href ?? (l?.repo ? `${ROADMAP_URL}/tree/main/${l.repo}` : undefined);
      return { key, isCode: c.includes("`"), cH: await inline(c), mean: strip(mean), ask: strip(ask), href };
    }),
  );

  return (
    <>
      <Crumb items={[["홈", "/"], ["용어 사전"]]} />
      <PageHead icon={<Ict n="book-a" size="lg" />} title="용어 사전" lede="기술 용어를 외우기보다 어떤 결정과 위험을 가리키는지 봐요." />
      <GlossaryTools counts={counts} />
      <div className="gl-grid" id="glo">
        {rows.map((x) => (
          <section key={x.id} id={x.id} className="gl-card" data-g={x.g} data-q={x.q}>
            <h2 dangerouslySetInnerHTML={{ __html: x.termH }} />
            <p className="gl-mean" dangerouslySetInnerHTML={{ __html: x.meanH }} />
            <p className="gl-ask">
              <Ic n="message-circle-question-mark" />
              <span dangerouslySetInnerHTML={{ __html: x.askH }} />
            </p>
            {(x.link.topics?.length || x.link.chapters?.length) && (
              <div className="gl-links">
                {x.link.topics?.map((slug) => {
                  const t = topicBySlug(slug);
                  return (
                    <Link key={slug} className="chip gl-topic" href={`/roadmap/${slug}/`}>
                      {AREA_IC[slug] ? <Ict n={AREA_IC[slug]} size="sm" /> : <NumBox>{`${t.stage}.${t.n}`}</NumBox>}
                      {t.t}
                    </Link>
                  );
                })}
                {x.link.chapters?.map((n) => {
                  const c = byNo.get(n)!;
                  return (
                    <Link key={n} className="chip" href={`/chapters/${c.dir}/`} title={`${n} ${c.title}`}>
                      <Logo k={chapterLogo(n, c.track)} size={18} />
                      {n}
                    </Link>
                  );
                })}
              </div>
            )}
          </section>
        ))}
      </div>

      <section className="sec">
        <SecHead title="로드맵 코드 한눈에 보기" />
        <div className="gl-codes">
          {codes.map((c) => {
            const inner = (
              <>
                {c.isCode ? <code dangerouslySetInnerHTML={{ __html: c.cH.replace(/<\/?code>/g, "") }} /> : <span className="gl-cname">{c.key}</span>}
                <b>{c.mean}</b>
                <small>
                  <Ic n="message-circle-question-mark" />
                  {c.ask}
                </small>
              </>
            );
            return c.href ? (
              <a key={c.key} className="tile" href={c.href} {...(/^https?:/.test(c.href) ? { target: "_blank", rel: "noopener" } : {})}>
                {inner}
              </a>
            ) : (
              <div key={c.key} className="tile">
                {inner}
              </div>
            );
          })}
        </div>
        {codeNote && <p className="gl-note">{codeNote}</p>}
      </section>

      <p className="note gl-src">
        원본: <a href={ghBlob(SRC)}>{SRC}</a> (로드맵 레포, MIT). 용어와 이어지는 주제, 강의는 이 사이트가 붙였어요.
      </p>
    </>
  );
}
