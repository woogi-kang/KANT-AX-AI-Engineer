// 챕터마다 다루는 도구의 로고를 정해요.
// 로고 모양은 Simple Icons(CC0)에서 가져오고, 각 상표는 상표권자의 것이에요.
// 도구를 가리키는 데만 쓰고 모양과 색을 바꾸지 않아요(이용 안내에 적어 둬요).
import * as si from "simple-icons";

export type Logo = { title: string; hex: string; path: string; viewBox: string; lucide?: "terminal" | "database" };

type SimpleIcon = { title: string; hex: string; path: string };
const brand = (i: SimpleIcon): Logo => ({ title: i.title, hex: `#${i.hex}`, path: i.path, viewBox: "0 0 24 24" });

// Simple Icons에 없는 것은 Lucide(ISC) 선 아이콘으로 그려요
const TERMINAL: Logo = { title: "터미널", hex: "#2B313D", path: "", viewBox: "0 0 24 24", lucide: "terminal" };
const DATABASE: Logo = { title: "데이터베이스", hex: "#A23B72", path: "", viewBox: "0 0 24 24", lucide: "database" };

export const LOGOS = {
  terminal: TERMINAL,
  database: DATABASE,
  git: brand(si.siGit),
  github: brand(si.siGithub),
  uv: brand(si.siUv),
  jupyter: brand(si.siJupyter),
  python: brand(si.siPython),
  docker: brand(si.siDocker),
  nginx: brand(si.siNginx),
  mysql: brand(si.siMysql),
  postgresql: brand(si.siPostgresql),
  numpy: brand(si.siNumpy),
  pandas: brand(si.siPandas),
} as const;
export type LogoKey = keyof typeof LOGOS;

const BY_CHAPTER: Record<string, LogoKey> = {
  "01": "terminal",
  "09": "uv",
  "10": "jupyter",
  "11": "github",
  "31": "nginx",
  "32": "database",
  "33": "mysql",
  "34": "postgresql",
  "44": "python",
  "45": "numpy",
  "46": "pandas",
};
const BY_TRACK: Record<string, LogoKey> = {
  터미널: "terminal",
  Git: "git",
  GitHub: "github",
  파이썬: "python",
  Docker: "docker",
  데이터베이스: "postgresql",
};

// 썸네일 구석에 같이 그릴 두 번째 도구
const SECOND: Record<string, LogoKey> = { "31": "docker", "33": "docker", "34": "docker", "44": "postgresql", "45": "pandas", "46": "python", "06": "github", "28": "python" };
export function chapterLogos(no: string, track: string): LogoKey[] {
  const a = chapterLogo(no, track);
  const b = SECOND[no];
  return b && b !== a ? [a, b] : [a];
}

export function chapterLogo(no: string, track: string): LogoKey {
  return BY_CHAPTER[no] ?? BY_TRACK[track] ?? "terminal";
}

/** 단계마다 대표 로고(나오는 순서대로, 겹치지 않게) */
export function stageLogos(chapters: { no: string; track: string }[]): LogoKey[] {
  const out: LogoKey[] = [];
  for (const c of chapters) {
    const k = chapterLogo(c.no, c.track);
    if (!out.includes(k)) out.push(k);
  }
  return out;
}
