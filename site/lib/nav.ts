// 왼쪽 목차와 찾기 창에 넘길 데이터를 만들어요(빌드할 때 한 번).
import { load } from "./content";
import { roadmap } from "./roadmap";
import { logosOf, chapterLogo, type LogoKey } from "./logos";
import { STAGE_IC, AREA_IC, LIB_IC, LIB_HREF, LIB_NAME, stageShort, type LibKey } from "./site";

export type NavData = {
  roadmap: { no: number; title: string; icon: string; topics: { href: string; t: string; n: string }[] }[];
  lectures: { no: number; title: string; logo: LogoKey; chapters: { href: string; no: string; t: string }[] }[];
  tips: number;
  library: { key: LibKey; title: string; icon: string; href: string }[];
};

export function navData(): NavData {
  const { stages, chapters, extras } = load();
  const r = roadmap();
  return {
    roadmap: r.stages.map((s) => ({
      no: s.no,
      title: stageShort(s.title),
      icon: STAGE_IC[s.no],
      topics:
        s.no === 5
          ? r.cases.map((c, n) => ({ href: `/library/cases/${c.id}/`, t: c.t, n: `${s.no}.${n + 1}` }))
          : s.topics.map((t) => ({ href: `/roadmap/${t.slug}/`, t: t.t, n: `${s.no}.${t.n}` })),
    })),
    lectures: stages.map((s) => {
      const list = chapters.filter((c) => c.stageNo === s.no);
      return { no: s.no, title: s.title, logo: logosOf(list)[0] ?? chapterLogo(list[0].no, list[0].track), chapters: list.map((c) => ({ href: `/chapters/${c.dir}/`, no: c.no, t: c.title })) };
    }),
    tips: extras.length,
    library: (Object.keys(LIB_IC) as LibKey[]).map((k) => ({ key: k, title: LIB_NAME[k], icon: LIB_IC[k], href: LIB_HREF[k] })),
  };
}
export { AREA_IC };
