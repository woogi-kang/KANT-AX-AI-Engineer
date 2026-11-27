// 사례 조직의 로고 칸이에요. Simple Icons(CC0)에 공식 브랜드 마크가 있으면 그 마크를 그 회사 색으로,
// 없으면 이름 첫 글자(공공기관은 건물 아이콘)를 보여 줘요. 로고는 사례를 알아보는 데만 써요.
import * as si from "simple-icons";
import { Landmark } from "lucide-react";
import { ORG_LOGO, isPublicOrg } from "@/lib/library";

type Icon = { title: string; path: string; hex: string };
const icon = (slug?: string): Icon | null => {
  if (!slug) return null;
  const k = `si${slug[0].toUpperCase()}${slug.slice(1)}` as keyof typeof si;
  const v = si[k] as unknown as Icon | undefined;
  return v?.path ? v : null;
};
const lum = (hex: string) => {
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
/** 첫 글자: 앞의 대문자 묶음(SK, HSAD, IBM), 영어는 두 낱말 머리글자, 한글은 첫 글자 */
export const initials = (org: string) => {
  const o = org.replace(/\s*\([^)]*\)\s*/g, "").split(/\s*·\s*/)[0].trim();
  const caps = /^[A-Z]{2,4}(?![a-z])/.exec(o);
  if (caps) return caps[0];
  if (/^[A-Za-z]/.test(o)) return o.split(/\s+/).slice(0, 2).map((w) => w[0].toUpperCase()).join("");
  return o[0] ?? "?";
};
/** 가로로 긴 워드마크는 칸을 넓게 써요 */
const WIDE = new Set(["samsung", "siemens", "lg", "cnet", "klarna", "zillow"]);
const TONES = ["a", "b", "c", "d"];
const tone = (s: string) => TONES[[...s].reduce((a, c) => a + c.charCodeAt(0), 0) % TONES.length];

export default function OrgMark({ id, org, size = "md" }: { id: string; org: string; size?: "sm" | "md" | "lg" }) {
  const ic = icon(ORG_LOGO[id]);
  if (ic) {
    const light = lum(ic.hex) > 0.6;
    return (
      <span className={`om om-${size} om-logo${light ? " om-fill" : ""}${WIDE.has(ORG_LOGO[id]) ? " om-wide" : ""}`} style={light ? { background: `#${ic.hex}` } : undefined} title={`${ic.title} 로고`}>
        <svg viewBox="0 0 24 24" role="img" aria-label={`${ic.title} 로고`} fill={light ? "#17120f" : `#${ic.hex}`}>
          <path d={ic.path} />
        </svg>
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
