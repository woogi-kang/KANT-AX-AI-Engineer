/** 사이트 로고: 쌓인 세 칸(풀스택)과 반짝임(AI). */
export default function BrandMark({ size = 28 }: { size?: number }) {
  return (
    <svg className="brand-mark" width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
      <rect width="32" height="32" rx="8" fill="var(--accent)" />
      <rect x="7" y="20" width="18" height="4" rx="2" fill="var(--accent-ink)" />
      <rect x="7" y="14" width="13" height="4" rx="2" fill="var(--accent-ink)" opacity=".8" />
      <rect x="7" y="8" width="8" height="4" rx="2" fill="var(--accent-ink)" opacity=".6" />
      <path d="M23 6.5l1.2 2.8 2.8 1.2-2.8 1.2L23 14.5l-1.2-2.8-2.8-1.2 2.8-1.2z" fill="var(--accent-ink)" />
    </svg>
  );
}
