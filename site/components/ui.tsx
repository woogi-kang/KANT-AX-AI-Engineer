// 여러 화면이 같이 쓰는 작은 조각이에요. 서버에서 그리는 컴포넌트예요(브라우저 쪽 컴포넌트에서는 lucide-react를 직접 불러요).
import Link from "next/link";
import { icons, ChevronRight } from "lucide-react";
import { LOGOS, logoSrc, type LogoKey } from "@/lib/logos";

export type IconName = string;
const pascal = (n: string) => n.replace(/(^|-)([a-z0-9])/g, (_, __, c: string) => c.toUpperCase());

/** lucide 아이콘을 이름(kebab-case)으로 그려요 */
export function Ic({ n, className = "i" }: { n: IconName; className?: string }) {
  const C = icons[pascal(n) as keyof typeof icons];
  if (!C) throw new Error(`없는 아이콘 ${n}`);
  return <C className={className} aria-hidden="true" />;
}

/** 아이콘 칸. size: sm, lg / tone: n(회색) */
export function Ict({ n, size, tone }: { n: IconName; size?: "sm" | "lg"; tone?: "n" }) {
  return (
    <span className={["ict", size, tone].filter(Boolean).join(" ")}>
      <Ic n={n} />
    </span>
  );
}
/** 번호 칸(예: 3.4) */
export function NumBox({ children }: { children: React.ReactNode }) {
  return <span className="ict sm n num">{children}</span>;
}

const DARK: LogoKey[] = ["github", "terminal"];
/** 도구 로고 그림 */
export function Logo({ k, size = 28 }: { k: LogoKey; size?: number }) {
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img className={DARK.includes(k) ? "lg dk" : "lg"} src={logoSrc(k)} alt={LOGOS[k].title} title={LOGOS[k].title} width={size} height={size} style={{ "--s": `${size}px` } as React.CSSProperties} />
  );
}
export function Logos({ ks, size = 28 }: { ks: LogoKey[]; size?: number }) {
  return (
    <span className="lgs">
      {ks.map((k) => (
        <Logo key={k} k={k} size={size} />
      ))}
    </span>
  );
}

/** 챕터 표지 그림 주소 */
export const coverSrc = (no: string) => `/img/covers/${no}.jpg`;
export const extraCoverSrc = (dir: string) => `/img/covers/x-${dir}.jpg`;
export function Cover({ src, alt = "" }: { src: string; alt?: string }) {
  // eslint-disable-next-line @next/next/no-img-element
  return <img className="cv" src={src} alt={alt} loading="lazy" width={480} height={270} />;
}

/** 펼쳐 보기 */
export function More({ label, children, open }: { label: React.ReactNode; children: React.ReactNode; open?: boolean }) {
  return (
    <details className="more" open={open}>
      <summary>
        <ChevronRight aria-hidden="true" />
        {label}
      </summary>
      <div>{children}</div>
    </details>
  );
}

/** 현재 위치 */
export function Crumb({ items }: { items: [string, string?][] }) {
  return (
    <nav className="crumb" aria-label="현재 위치">
      {items.map(([t, h], n) => (
        <span key={n} style={{ display: "contents" }}>
          {h ? <Link href={h}>{t}</Link> : <span aria-current="page">{t}</span>}
          {n < items.length - 1 && <ChevronRight aria-hidden="true" />}
        </span>
      ))}
    </nav>
  );
}

/** 화면 머리: 아이콘(또는 로고)과 제목, 한 줄 설명 */
export function PageHead({ icon, eyebrow, title, lede }: { icon?: React.ReactNode; eyebrow?: React.ReactNode; title: React.ReactNode; lede?: React.ReactNode }) {
  return (
    <>
      <div className="th">
        {icon}
        <div>
          {eyebrow && <span className="eyebrow">{eyebrow}</span>}
          <h1>{title}</h1>
        </div>
      </div>
      {lede && <p className="lede">{lede}</p>}
    </>
  );
}

/** 절 머리 */
export function SecHead({ title, right, as: H = "h2" }: { title: React.ReactNode; right?: React.ReactNode; as?: "h2" | "h3" }) {
  return (
    <div className="sh">
      <H>{title}</H>
      {right}
    </div>
  );
}

/** 아직 만들지 않은 화면 */
export function Soon({ children = "이 화면은 만들고 있어요." }: { children?: React.ReactNode }) {
  return <p className="soonbox">{children}</p>;
}

/** 난이도 막대(1~5) */
export function Diff({ v, max = 5 }: { v: number; max?: number }) {
  return (
    <span className="diff" title={`난이도 ${v} / ${max}`} aria-label={`난이도 ${v} / ${max}`}>
      {Array.from({ length: max }, (_, k) => (
        <i key={k} className={k < v ? "on" : ""} />
      ))}
    </span>
  );
}
