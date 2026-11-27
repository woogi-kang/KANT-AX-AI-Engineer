// 사례 조직의 로고 칸이에요. 로고 파일(assets/orgs/, 출처는 SOURCES.md)이 있으면 칸에 맞춰 줄여 보여 주고,
// 없으면 이름 첫 글자(해외 공공기관은 건물 아이콘)를 보여 줘요. 로고는 어느 조직의 사례인지 알아보는 데만 써요.
import { Landmark } from "lucide-react";
import { ORG_LOGO, ORG_NAME, ORG_WIDE, isPublicOrg } from "@/lib/library";

/** 첫 글자: 앞의 대문자 묶음(SK, HSAD, IBM), 영어는 두 낱말 머리글자, 한글은 첫 글자 */
export const initials = (org: string) => {
  const o = org.replace(/\s*\([^)]*\)\s*/g, "").split(/\s*·\s*/)[0].trim();
  const caps = /^[A-Z]{2,4}(?![a-z])/.exec(o);
  if (caps) return caps[0];
  if (/^[A-Za-z]/.test(o)) return o.split(/\s+/).slice(0, 2).map((w) => w[0].toUpperCase()).join("");
  return o[0] ?? "?";
};
const TONES = ["a", "b", "c", "d"];
const tone = (s: string) => TONES[[...s].reduce((a, c) => a + c.charCodeAt(0), 0) % TONES.length];

export default function OrgMark({ id, org, size = "md" }: { id: string; org: string; size?: "sm" | "md" | "lg" }) {
  const f = ORG_LOGO[id];
  if (f) {
    const name = ORG_NAME[f] ?? org.replace(/\s*\([^)]*\)\s*/g, "");
    return (
      <span className={`om om-${size} om-logo${ORG_WIDE.has(f) ? " om-wide" : ""}`} title={`${name} 로고`}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={`/img/orgs/${f}.svg`} alt={`${name} 로고`} loading="lazy" decoding="async" />
      </span>
    );
  }
  if (isPublicOrg(org))
    return (
      <span className={`om om-${size} om-t-gov`} aria-hidden="true">
        <Landmark />
      </span>
    );
  const t = initials(org);
  return (
    <span className={`om om-${size} om-t-${tone(org)}${t.length > 2 ? " om-long" : ""}`} aria-hidden="true">
      {t}
    </span>
  );
}
