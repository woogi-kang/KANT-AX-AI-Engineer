// 챕터마다 다루는 도구의 로고를 정해요. 브라우저 쪽 컴포넌트도 쓰니 node 모듈을 쓰지 않아요.
// 그림은 assets/logos/에 있어요: devicon(MIT)의 공식 컬러 로고, uv는 Simple Icons(CC0), 데이터베이스는 Lucide(ISC) 모양.
// 도구를 가리키는 데만 쓰고 모양과 색을 바꾸지 않아요(이용 안내에 적어 둬요).

export const LOGOS = {
  terminal: { title: "터미널", file: "bash" },
  git: { title: "Git", file: "git" },
  github: { title: "GitHub", file: "github" },
  uv: { title: "uv", file: "uv" },
  jupyter: { title: "Jupyter", file: "jupyter" },
  python: { title: "Python", file: "python" },
  docker: { title: "Docker", file: "docker" },
  nginx: { title: "nginx", file: "nginx" },
  database: { title: "데이터베이스", file: "database" },
  mysql: { title: "MySQL", file: "mysql" },
  postgresql: { title: "PostgreSQL", file: "postgresql" },
  numpy: { title: "NumPy", file: "numpy" },
  pandas: { title: "pandas", file: "pandas" },
} as const;
export type LogoKey = keyof typeof LOGOS;
export const logoSrc = (k: LogoKey) => `/img/logos/${LOGOS[k].file}.svg`;

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
const SECOND: Record<string, LogoKey> = { "06": "github", "31": "docker", "33": "docker", "34": "docker", "44": "postgresql", "45": "pandas" };
const BY_TRACK: Record<string, LogoKey> = {
  터미널: "terminal",
  Git: "git",
  GitHub: "github",
  파이썬: "python",
  Docker: "docker",
  데이터베이스: "postgresql",
};

/** 챕터의 로고(대표 하나, 있으면 둘째) */
export function chapterLogos(no: string, track: string): LogoKey[] {
  const a = BY_CHAPTER[no] ?? BY_TRACK[track] ?? "terminal";
  const b = SECOND[no];
  return b ? [a, b] : [a];
}
export const chapterLogo = (no: string, track: string) => chapterLogos(no, track)[0];

/** 여러 챕터의 대표 로고를 나오는 순서대로, 겹치지 않게 */
export function logosOf(chapters: { no: string; track: string }[]): LogoKey[] {
  // 많이 나오는 로고부터(같으면 먼저 나온 순서). 단계 맨 앞 챕터가 그 단계 대표가 아닐 때도 있어서요(예: 파이썬 단계의 09 uv)
  const out: LogoKey[] = [];
  const n = new Map<LogoKey, number>();
  for (const c of chapters)
    for (const k of chapterLogos(c.no, c.track)) {
      if (!out.includes(k)) out.push(k);
      n.set(k, (n.get(k) ?? 0) + 1);
    }
  return out.map((k, i) => [k, i] as const).sort((a, b) => n.get(b[0])! - n.get(a[0])! || a[1] - b[1]).map(([k]) => k);
}
