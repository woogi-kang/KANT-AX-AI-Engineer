import type { Metadata } from "next";
import fs from "node:fs";
import path from "node:path";
import Link from "next/link";
import { load } from "@/lib/content";
import { roadmap, readRm, strip, sections, mapRoadmapLink, ghBlob, topicBySlug } from "@/lib/roadmap";
import { renderRoadmapMd } from "@/lib/markdown";
import { START } from "@/lib/home";
import { AREA_IC, caseIcon } from "@/lib/site";
import { Crumb, Ic, Ict, More, NumBox, PageHead, SecHead } from "@/components/ui";
import LecCard from "@/components/LecCard";
import "./start.css";

export const metadata: Metadata = { title: "시작하기", description: "지금 나와 가까운 길을 골라 처음 할 일과 이어서 볼 주제, 강의를 봐요." };

type PathCfg = { start: number; route?: number; case?: string; topics: string[]; chapters: string[]; chaptersWhy?: string };
const ENTRY = "learning-paths/entry-routes.md";

function entryRoutes() {
  const md = readRm(ENTRY);
  const block = md.split("## 내 경험과 가까운 경로")[1]?.split("\n## ")[0] ?? "";
  const rows = block
    .split("\n")
    .filter((l) => /^\|/.test(l) && !/^\|[\s|:-]+\|$/.test(l))
    .slice(1)
    .map((l) => l.slice(1, -1).split(" | ").map((c) => strip(c.replace(/^\|\s*/, ""))));
  const detail = sections(md).filter((s) => /^\d\. /.test(s.title));
  return { rows, detail };
}

export default async function StartPage() {
  const r = roadmap();
  const byNo = new Map(load().chapters.map((c) => [c.no, c]));
  const cfg = JSON.parse(fs.readFileSync(path.join(process.cwd(), "content", "start-paths.json"), "utf8")).paths as Record<string, PathCfg>;
  const { rows, detail } = entryRoutes();
  const runbook = readRm("case-studies/beauty-d2c-voc/RUNBOOK.md");
  const runCmd = /## 실행[\s\S]*?```bash\n([^\n]+)\n```/.exec(runbook)?.[1] ?? "";
  const keys = ["new", "dev", "biz", "run"] as const;
  const paths = await Promise.all(
    keys.map(async (key) => {
      const c = cfg[key];
      const st = START.find((x) => x.key === key)!;
      const s = r.start[c.start];
      const row = c.route !== undefined ? rows[c.route] : undefined;
      const det = c.route !== undefined ? detail[c.route] : undefined;
      const detHtml = det ? await renderRoadmapMd(ENTRY, det.body) : "";
      const cs = c.case ? r.cases.find((x) => x.id === c.case) : undefined;
      return { key, c, st, s, row, det, detHtml, cs };
    }),
  );
  return (
    <>
      <Crumb items={[["홈", "/"], ["시작하기"]]} />
      <PageHead icon={<Ict n="signpost" size="lg" />} title="어디서 시작할까요?" lede="지금 나와 가까운 길을 골라요. 처음 할 일과 이어서 볼 주제, 강의가 있어요." />
      <div className="tiles t6 st-pick">
        {START.map((x) => (
          <Link key={x.key} className="tile c" href={x.href}>
            <Ict n={x.icon} size="lg" />
            <b>{x.label}</b>
          </Link>
        ))}
      </div>
      <Link className="use st-p1" href="/roadmap/01-safe-assistant/">
        <Ict n="flag" />
        <span>
          <small>어느 길이든 첫 실습은 같아요</small>
          <b>P1 · 안전한 보조 도구</b>
        </span>
        <span className="go">
          <Ic n="arrow-right" />
        </span>
      </Link>

      {paths.map(({ key, c, st, s, row, det, detHtml, cs }) => (
        <section key={key} id={key} className="stage st-path">
          <div className="th">
            <Ict n={st.icon} size="lg" />
            <div>
              <span className="eyebrow">{s.who}</span>
              <h2>{st.label}</h2>
            </div>
          </div>

          <ol className="st-steps">
            {row && (
              <li>
                <span className="sn">1</span>
                <small>먼저 채울 것</small>
                <b>{row[1]}</b>
              </li>
            )}
            {row && (
              <li>
                <span className="sn">2</span>
                <small>시작할 실습</small>
                <b>{row[2]}</b>
              </li>
            )}
            {key === "run" && (
              <li className="wide">
                <span className="sn">1</span>
                <small>로드맵 레포 맨 위 폴더에서 실행</small>
                <code className="st-cmd">{runCmd}</code>
              </li>
            )}
            <li>
              <span className="sn">{key === "run" ? 2 : 3}</span>
              <small>첫 결과물</small>
              <b>{s.first}</b>
            </li>
          </ol>

          {cs && (
            <Link className="tp st-case" href={`/library/cases/${cs.id}/`}>
              <span className="hd">
                <Ict n={caseIcon(cs.area)} size="sm" tone="n" />
                <b>{cs.t}</b>
              </span>
              <span className="run">
                <Ic n="play" />
                실행 예제
              </span>
            </Link>
          )}

          {c.topics.length > 0 && (
            <div className="st-sub">
              <SecHead as="h3" title="이어서 볼 로드맵 주제" />
              <div className="tiles t3">
                {c.topics.map((slug) => {
                  const t = topicBySlug(slug);
                  return (
                    <Link key={slug} className="tp" href={`/roadmap/${slug}/`}>
                      <span className="hd">
                        {AREA_IC[slug] ? <Ict n={AREA_IC[slug]} size="sm" /> : <NumBox>{`${t.stage}.${t.n}`}</NumBox>}
                        <b>{t.t}</b>
                      </span>
                    </Link>
                  );
                })}
              </div>
            </div>
          )}

          {c.chapters.length > 0 && (
            <div className="st-sub">
              <SecHead as="h3" title="먼저 익힐 기초 강의" right={c.chaptersWhy ? <span className="cnt">{c.chaptersWhy}</span> : undefined} />
              <div className="tiles t4">
                {c.chapters.map((n) => (
                  <LecCard key={n} c={byNo.get(n)!} />
                ))}
              </div>
            </div>
          )}

          <More label="자세히 보기">
            {det && <div className="prose st-det" dangerouslySetInnerHTML={{ __html: detHtml }} />}
            <p className="st-links">
              {s.goLinks.map((l) => {
                const h = mapRoadmapLink("README.md", l.href);
                const ext = /^https?:/.test(h);
                return (
                  <a key={l.href} href={h} {...(ext ? { target: "_blank", rel: "noopener" } : {})}>
                    {l.t}
                    {ext && <Ic n="external-link" />}
                  </a>
                );
              })}
            </p>
          </More>
        </section>
      ))}

      <p className="note st-src">
        원본: 로드맵 레포 <a href={ghBlob("README.md")}>README &quot;나에게 맞는 시작점&quot;</a>, <a href={ghBlob(ENTRY)}>{ENTRY}</a>
      </p>
    </>
  );
}
