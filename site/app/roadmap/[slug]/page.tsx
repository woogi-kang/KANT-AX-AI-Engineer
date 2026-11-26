import type { Metadata } from "next";
import Link from "next/link";
import { load, type Chapter } from "@/lib/content";
import { roadmap, topicBySlug, ghBlob, ROADMAP_URL, type Topic } from "@/lib/roadmap";
import { links, topicChapters } from "@/lib/links";
import { chapterLogo } from "@/lib/logos";
import { AREA_IC, STAGE_IC, stageShort } from "@/lib/site";
import { topicSections, findSec, listOf, firstPara, secHtml, firstFlow, flowMarkup, templateLinks, docCards, type Sec } from "@/lib/topic";
import { Crumb, Ic, Ict, Logo, More, NumBox, SecHead } from "@/components/ui";
import LecCard from "@/components/LecCard";
import OpenOnHash from "./OpenOnHash";
import "./topic.css";

type Params = { params: Promise<{ slug: string }> };
export const dynamicParams = false;
export function generateStaticParams() {
  return roadmap().topics.map((t) => ({ slug: t.slug }));
}
export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const t = topicBySlug((await params).slug);
  return { title: `${t.t} · 로드맵`, description: t.q };
}

const code = (t: Topic) => `${t.stage}.${t.n}`;
function TopicIcon({ t, size }: { t: Topic; size?: "sm" | "lg" }) {
  if (AREA_IC[t.slug]) return <Ict n={AREA_IC[t.slug]} size={size} />;
  return size === "lg" ? <span className="ict lg n num tpnum">{code(t)}</span> : <NumBox>{code(t)}</NumBox>;
}

function Chips({ nos, byNo }: { nos: string[]; byNo: Map<string, Chapter> }) {
  if (!nos.length) return <em className="kn-soon">강의 준비 중</em>;
  return (
    <span className="chips kn-chips">
      {nos.map((n) => {
        const c = byNo.get(n)!;
        return (
          <Link key={n} className="chip" href={`/chapters/${c.dir}/`} title={`${n} ${c.title}`}>
            <Logo k={chapterLogo(n, c.track)} size={18} />
            {n}
          </Link>
        );
      })}
    </span>
  );
}

function CheckCols({ pass, stop, passTitle, stopTitle }: { pass?: Sec; stop?: Sec; passTitle: string; stopTitle: string }) {
  if (!pass && !stop) return null;
  return (
    <section className="sec">
      <div className="ckcols">
        {pass && (
          <div className="ck ok">
            <h3>
              <Ic n="circle-check" />
              {passTitle}
            </h3>
            <ul>
              {listOf(pass.md).map((x) => (
                <li key={x}>{x}</li>
              ))}
            </ul>
          </div>
        )}
        {stop && (
          <div className="ck stop">
            <h3>
              <Ic n="octagon-x" />
              {stopTitle}
            </h3>
            <ul>
              {listOf(stop.md).map((x) => (
                <li key={x}>{x}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}

export default async function TopicPage({ params }: Params) {
  const t = topicBySlug((await params).slug);
  const r = roadmap();
  const stage = r.stages[t.stage - 1];
  const byNo = new Map(load().chapters.map((c) => [c.no, c]));
  const { intro, secs } = topicSections(t);
  const link = links().byTopic[t.slug];
  const nos = topicChapters(t.slug);
  const used = new Set<Sec>();
  const take = (re: RegExp) => {
    const s = findSec(secs, re);
    if (s) used.add(s);
    return s;
  };

  /* 단계마다 앞에 꺼내 보일 것 */
  let ask = t.q ?? "";
  let lead: { label: string; md: string } | null = intro ? { label: "이 문서는", md: intro } : null;
  let know: { items: string[]; sec: Sec } | null = null;
  let outputs: string[] = [];
  let outputsTitle = "";
  let pass: Sec | undefined, stop: Sec | undefined;
  let passTitle = "통과 기준";
  let stopTitle = "중단 신호";
  let flow = null as ReturnType<typeof firstFlow>;
  let flowTitle = "";

  if (t.kind === "area") {
    const why = take(/^왜 필요한가/);
    if (why) lead = { label: "왜 필요한가", md: why.md };
    const k = take(/^알아야 할 것/);
    if (k) know = { items: listOf(k.md), sec: k };
  }
  if (t.kind === "step") {
    const goal = take(/^목적/);
    if (goal) {
      const p1 = firstPara(goal.md);
      const cut = p1.indexOf(". ");
      ask = cut > 0 ? p1.slice(0, cut + 1) : p1;
      const more = cut > 0 ? p1.slice(cut + 2) : "";
      const rest = [more, ...goal.md.split("\n\n").slice(1)].join("\n\n").trim();
      lead = rest ? { label: "목적 자세히", md: rest } : null;
    }
    const out = take(/^산출물/);
    outputs = listOf(out?.md);
    outputsTitle = "만들 산출물";
    pass = take(/^통과 기준/);
    stop = take(/^중단 신호/);
  }
  if (t.kind === "project") {
    const goal = take(/^목표$/);
    if (goal) {
      const p1 = firstPara(goal.md);
      const cut = p1.indexOf(". ");
      ask = cut > 0 ? p1.slice(0, cut + 1) : p1;
      const more = cut > 0 ? p1.slice(cut + 2) : "";
      const rest = [more, ...goal.md.split("\n\n").slice(1)].join("\n\n").trim();
      lead = rest ? { label: "목표 자세히", md: rest } : null;
    }
    const fs = findSec(secs, /^업무 흐름/);
    flow = fs ? firstFlow(fs.md) : null;
    if (flow && fs) {
      used.add(fs);
      flowTitle = "업무 흐름";
    }
    const out = take(/^확인할 결과/);
    outputs = listOf(out?.md);
    outputsTitle = "확인할 결과";
    pass = take(/^통과 기준/);
    stop = take(/^중단 조건/);
    stopTitle = "중단 조건";
  }
  if (t.kind === "doc") {
    const all = secs.map((s) => s.md).join("\n");
    flow = firstFlow(all);
    if (flow) flowTitle = findSec(secs, /책임의 끝/)?.title.replace(/^\d+\.\s*/, "") ?? (t.slug === "competency-map" ? "영역이 이어지는 순서" : "반복해서 나타난 공통 책임");
  }
  const cards = t.kind === "doc" ? docCards(t, secs) : null;
  const rest = secs.map((s, n) => ({ s, n })).filter(({ s }) => !used.has(s));
  const restHtml = await Promise.all(rest.map(({ s }) => secHtml(t, s.md)));
  const leadHtml = lead ? await secHtml(t, lead.md) : "";
  const tmpls = templateLinks(t);
  const siblings = stage.topics;
  const i = r.topics.indexOf(t);
  const prev = r.topics[i - 1];
  const next = r.topics[i + 1];

  return (
    <div className="tpc">
      <Crumb items={[["로드맵", "/roadmap/"], [`${t.stage}. ${stageShort(stage.title)}`, `/roadmap/#stage-${t.stage}`], [t.t]]} />
      <div className="th">
        <TopicIcon t={t} size="lg" />
        <div>
          <span className="eyebrow">
            {t.stage}단계 · {stage.title}
          </span>
          <h1>{t.t}</h1>
        </div>
      </div>
      {ask && <p className="ask">{ask}</p>}
      {lead && (
        <More label={lead.label}>
          <div className="prose" dangerouslySetInnerHTML={{ __html: leadHtml }} />
        </More>
      )}

      <nav className="sibs" aria-label={`${t.stage}단계 주제`}>
        {siblings.map((s) => (
          <Link key={s.slug} href={`/roadmap/${s.slug}/`} aria-current={s.slug === t.slug ? "page" : undefined}>
            <TopicIcon t={s} size="sm" />
            <span>{s.t}</span>
          </Link>
        ))}
      </nav>

      {t.kind === "project" && (
        <section className="sec">
          <div className="goal2">
            <div className="tile big">
              <Ict n="package-check" />
              <small>목표 결과물</small>
              <b>{t.q}</b>
            </div>
            <div className="tile big">
              <Ict n="file-check" />
              <small>다음 단계로 가기 전에 필요한 근거</small>
              <b>{t.need}</b>
            </div>
          </div>
        </section>
      )}

      {flow && (
        <section className="sec">
          <SecHead title={flowTitle} />
          <div dangerouslySetInnerHTML={{ __html: flowMarkup(flow) }} />
        </section>
      )}

      {cards && (
        <section className="sec">
          <SecHead title={cards.title} right={<span className="cnt">{cards.cards.length}개</span>} />
          <div className={`tiles t${cards.cols} dcards`}>
            {cards.cards.map((c) =>
              c.id ? (
                <a key={c.t} className="tile" href={`#${c.id}`}>
                  <b>{c.t}</b>
                  {c.d && <small>{c.d}</small>}
                </a>
              ) : (
                <div key={c.t} className="tile">
                  <b>{c.t}</b>
                  {c.d && <small>{c.d}</small>}
                </div>
              ),
            )}
          </div>
        </section>
      )}

      {nos.length > 0 ? (
        <section className="sec">
          <SecHead title="먼저 익힐 기초 강의" right={<span className="cnt">{nos.length}챕터</span>} />
          <div className="tiles t4">
            {nos.map((n) => (
              <LecCard key={n} c={byNo.get(n)!} />
            ))}
          </div>
          {link?.soon && <p className="soonline">강의 준비 중: {link.soon}</p>}
        </section>
      ) : link?.soon ? (
        <section className="sec">
          <SecHead title="먼저 익힐 기초 강의" />
          <p className="soonbox">강의 준비 중: {link.soon}</p>
        </section>
      ) : null}

      {know && (
        <section className="sec">
          <SecHead title="알아야 할 것" right={<span className="cnt">{know.items.length}가지</span>} />
          <div className="know">
            {know.items.map((k, n) => (
              <div key={k} className="kn">
                <span>{k}</span>
                {(link?.know ?? []).some((x) => x.length) && <Chips nos={link?.know?.[n] ?? []} byNo={byNo} />}
              </div>
            ))}
          </div>
        </section>
      )}

      {outputs.length > 0 && (
        <section className="sec">
          <SecHead title={outputsTitle} right={<span className="cnt">{outputs.length}가지</span>} />
          <div className="tiles t3 outs">
            {outputs.map((o) => (
              <div key={o} className="tile">
                <Ic n="file-text" />
                <span>{o}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      <CheckCols pass={pass} stop={stop} passTitle={passTitle} stopTitle={stopTitle} />

      {tmpls.length > 0 && (
        <section className="sec">
          <SecHead title="같이 쓰는 양식" />
          <div className="tmpls">
            {tmpls.map((x) => (
              <Link key={x.slug} className="tile" href={`/library/templates/${x.slug}/`}>
                <Ict n="clipboard-check" size="sm" />
                <b>{x.t}</b>
              </Link>
            ))}
          </div>
        </section>
      )}

      <section className="sec doc">
        <SecHead
          title={t.kind === "doc" ? "문서 읽기" : "더 읽기"}
          right={
            <a href={ghBlob(t.path)} target="_blank" rel="noopener">
              원문 <Ic n="external-link" />
            </a>
          }
        />
        {rest.map(({ s, n }, k) => (
          <details key={s.title} id={`sec-${n}`}>
            <summary>
              {s.title}
              <Ic n="chevron-down" />
            </summary>
            <div className="in prose" dangerouslySetInnerHTML={{ __html: restHtml[k] }} />
          </details>
        ))}
        <p className="src">
          <span>
            <Ic n="git-branch" />
            ax-engineer-roadmap {r.version}
          </span>
          <a href={`${ROADMAP_URL}/edit/main/${t.path}`} target="_blank" rel="noopener">
            <Ic n="pencil" />
            고치기 제안
          </a>
          <span>로드맵 레포의 글을 그대로 옮겼어요(MIT)</span>
        </p>
      </section>

      <nav className="pn tpn" aria-label="이전, 다음 주제">
        {prev ? (
          <Link href={`/roadmap/${prev.slug}/`}>
            <TopicIcon t={prev} />
            <span>
              <small>이전 주제</small>
              <b>{prev.t}</b>
            </span>
          </Link>
        ) : (
          <span className="empty" />
        )}
        {next ? (
          <Link className="r" href={`/roadmap/${next.slug}/`}>
            <TopicIcon t={next} />
            <span>
              <small>다음 주제</small>
              <b>{next.t}</b>
            </span>
          </Link>
        ) : (
          <Link className="r" href="/roadmap/#stage-5">
            <Ict n={STAGE_IC[5]} />
            <span>
              <small>다음 단계</small>
              <b>{`5. ${r.stages[4].title}`}</b>
            </span>
          </Link>
        )}
      </nav>
      <OpenOnHash />
    </div>
  );
}
