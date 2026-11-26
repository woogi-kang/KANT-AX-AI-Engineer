import { Database, SquareTerminal } from "lucide-react";
import type { Logo } from "@/lib/logos";

function Glyph({ logo, size }: { logo: Logo; size: number }) {
  if (logo.lucide === "terminal") return <SquareTerminal width={size} height={size} strokeWidth={1.8} />;
  if (logo.lucide === "database") return <Database width={size} height={size} strokeWidth={1.8} />;
  return (
    <svg viewBox={logo.viewBox} width={size} height={size} fill="currentColor" aria-hidden="true">
      <path d={logo.path} />
    </svg>
  );
}

/** 챕터 썸네일: 도구 색 바탕, 번호마다 다른 무늬, 가운데 큰 도구 로고. 그림 파일 없이 그려요. */
export default function Thumb({ no, logos, label, kw }: { no: string; logos: Logo[]; label?: string; kw?: string }) {
  const [a, b] = logos;
  const v = parseInt(no, 10) % 4;
  return (
    <div className={`thumb v${v}`} style={{ "--c": a.hex } as React.CSSProperties} aria-hidden="true">
      <svg className="pat" viewBox="0 0 320 180" preserveAspectRatio="xMidYMid slice">
        {v === 0 && [40, 80, 120, 160].map((r) => <circle key={r} cx="270" cy="150" r={r} />)}
        {v === 1 && Array.from({ length: 9 }, (_, i) => <line key={i} x1={i * 44 - 60} y1="190" x2={i * 44 + 60} y2="-10" />)}
        {v === 2 &&
          Array.from({ length: 8 * 5 }, (_, i) => <circle key={i} className="dot" cx={30 + (i % 8) * 38} cy={22 + Math.floor(i / 8) * 34} r="2.2" />)}
        {v === 3 && (
          <>
            <rect x="200" y="-40" width="160" height="160" rx="36" transform="rotate(18 280 40)" />
            <rect x="-40" y="110" width="120" height="120" rx="28" transform="rotate(-14 20 170)" />
          </>
        )}
      </svg>
      <span className="no">{no}</span>
      {label && <span className="lbl">{label}</span>}
      {kw && <span className="kw">{kw}</span>}
      <span className="main">
        <Glyph logo={a} size={64} />
      </span>
      {b && (
        <span className="sub" style={{ background: b.hex }}>
          <Glyph logo={b} size={18} />
        </span>
      )}
    </div>
  );
}
