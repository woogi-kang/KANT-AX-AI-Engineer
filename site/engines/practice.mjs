// practice.json 한 개를 읽는 법이에요. 화면(components/practice)과 자동 대조(scripts/practice-check.mjs)가 같이 써요.
// 칸 하나를 실행할 때는 같은 chain(같은 커널, 같은 psql 흐름)에서 앞에 있던 칸을 먼저 조용히 실행해요.

/** 이 칸 앞에 실행할 코드 목록 */
export function preludeOf(data, cell) {
  const out = [];
  for (const c of data.cells) {
    if (c.id === cell.id) break;
    if (c.chain === cell.chain && c.code) out.push(c.code);
  }
  return out;
}

/** 엔진에 보낼 묶음 */
export function jobOf(data, cell, code) {
  return {
    prelude: preludeOf(data, cell),
    code: code ?? cell.code,
    setup: cell.noseed ? undefined : data.setup,
    packages: data.packages,
    prompt: data.prompt,
  };
}
