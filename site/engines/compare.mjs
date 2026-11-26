// 내 출력과 수업 출력을 줄마다 견줘요. 줄 끝 빈칸과 맨 끝 빈 줄은 보지 않아요.
export function norm(lines) {
  // 메모리 주소(at 0x7f…)는 실행할 때마다 달라서 보지 않아요.
  const a = (lines || []).map((l) => String(l).replace(/\s+$/, "").replace(/ at 0x[0-9a-f]+/g, " at 0x…"));
  while (a.length && a[a.length - 1] === "") a.pop();
  return a;
}
/** 같으면 true. diff는 [{kind: "same"|"mine"|"class", text}] */
export function compare(mine, cls) {
  const a = norm(mine);
  const b = norm(cls);
  const same = a.length === b.length && a.every((x, i) => x === b[i]);
  return { same, a, b };
}
/** 줄 단위로 어디가 다른지 표시해요(같은 자리의 줄끼리). */
export function marks(a, b) {
  const n = Math.max(a.length, b.length);
  const ma = [];
  const mb = [];
  for (let i = 0; i < n; i++) {
    const d = a[i] !== b[i];
    if (i < a.length) ma.push(d);
    if (i < b.length) mb.push(d);
  }
  return { ma, mb };
}
