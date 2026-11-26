import { Database, SquareTerminal } from "lucide-react";
import type { Logo } from "@/lib/logos";

/** 도구 로고를 그 도구 색 칸 위에 흰색으로 그려요. size는 칸의 한 변(px)이에요. */
export default function LogoTile({ logo, size = 40, label = false }: { logo: Logo; size?: number; label?: boolean }) {
  const g = Math.round(size * 0.56);
  return (
    <span
      className="logo-tile"
      style={{ width: size, height: size, background: logo.hex, borderRadius: Math.round(size * 0.26) }}
      role={label ? "img" : undefined}
      aria-label={label ? logo.title : undefined}
      aria-hidden={label ? undefined : true}
      title={logo.title}
    >
      {logo.lucide === "terminal" ? (
        <SquareTerminal width={g} height={g} strokeWidth={2} />
      ) : logo.lucide === "database" ? (
        <Database width={g} height={g} strokeWidth={2} />
      ) : (
        <svg viewBox={logo.viewBox} width={g} height={g} fill="currentColor">
          <path d={logo.path} />
        </svg>
      )}
    </span>
  );
}
