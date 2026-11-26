// 브라우저 쪽 컴포넌트도 쓰는 값이라 node 모듈 없이 따로 둬요.
export const TRACKS = {
  터미널: "term",
  Git: "git",
  GitHub: "gh",
  파이썬: "py",
  Docker: "docker",
  데이터베이스: "db",
} as const;
export type TrackName = keyof typeof TRACKS;
export type TrackKey = (typeof TRACKS)[TrackName];

export const LEVELS = { 입문: 1, 기초: 2, 응용: 3 } as const;
export type LevelName = keyof typeof LEVELS;

