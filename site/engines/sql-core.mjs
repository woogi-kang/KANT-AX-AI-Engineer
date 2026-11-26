// SQL 실습 칸의 엔진 코드예요. 브라우저 워커(sql-worker.mjs)와 자동 대조(scripts/practice-check.mjs)가 같이 써요.
// PGlite(브라우저 안 PostgreSQL)로 문장을 하나씩 실행하고, 결과를 psql 화면 모양으로 그려요.

const RIGHT = new Set([20, 21, 23, 26, 28, 29, 700, 701, 790, 1700]); // 숫자 타입은 psql처럼 오른쪽 맞춤

/** 모든 타입을 글자 그대로 받아요(psql처럼 보여 주려고). */
export function rawParsers() {
  const p = {};
  for (let i = 0; i < 20000; i++) p[i] = (x) => x;
  return p;
}

/** 화면 칸 수: 한글과 한자는 두 칸이에요. */
export function dw(s) {
  let w = 0;
  for (const ch of s) {
    const c = ch.codePointAt(0);
    if (c === 0) continue;
    if (
      (c >= 0x1100 && c <= 0x115f) ||
      (c >= 0x2e80 && c <= 0xa4cf && c !== 0x303f) ||
      (c >= 0xac00 && c <= 0xd7a3) ||
      (c >= 0xf900 && c <= 0xfaff) ||
      (c >= 0xfe30 && c <= 0xfe4f) ||
      (c >= 0xff00 && c <= 0xff60) ||
      (c >= 0xffe0 && c <= 0xffe6) ||
      (c >= 0x1f300 && c <= 0x1faff) ||
      (c >= 0x20000 && c <= 0x3fffd)
    )
      w += 2;
    else w += 1;
  }
  return w;
}
const pad = (s, n) => s + " ".repeat(Math.max(0, n - dw(s)));
const lpad = (s, n) => " ".repeat(Math.max(0, n - dw(s))) + s;

/** psql의 기본(aligned) 표 모양 */
export function formatTable(fields, rows) {
  const n = fields.length;
  const lines = [];
  if (n === 0) {
    lines.push("--");
  } else {
    const cells = rows.map((r) => r.map((v) => (v === null || v === undefined ? "" : String(v))));
    const w = fields.map((f, i) => Math.max(dw(f.name), ...cells.map((r) => Math.max(...r[i].split("\n").map(dw)))));
    const right = fields.map((f) => RIGHT.has(f.dataTypeID));
    lines.push(
      fields
        .map((f, i) => {
          const sp = w[i] - dw(f.name);
          const l = Math.floor(sp / 2);
          const head = " ".repeat(l) + f.name + (i < n - 1 ? " ".repeat(sp - l) : "");
          return " " + head;
        })
        .join(" |")
        .replace(/\s+$/, "")
    );
    lines.push(w.map((x) => "-".repeat(x + 2)).join("+"));
    for (const r of cells) {
      const parts = r[0] !== undefined ? r : [];
      lines.push(
        parts
          .map((v, i) => {
            const last = i === n - 1;
            const s = right[i] ? lpad(v, w[i]) : last ? v : pad(v, w[i]);
            return " " + s;
          })
          .join(" |")
          .replace(/\s+$/, "")
      );
    }
  }
  lines.push(`(${rows.length} ${rows.length === 1 ? "row" : "rows"})`);
  lines.push("");
  return lines;
}

/** 문장을 ;로 나눠요. 따옴표, $$, 주석 안의 ;는 건너뛰어요. 끝에 ;가 없는 조각은 rest로 돌려줘요. */
export function splitSql(text) {
  const out = [];
  let i = 0;
  let start = 0;
  let depth = 0;
  const n = text.length;
  while (i < n) {
    const c = text[i];
    const d = text[i + 1];
    if (c === "-" && d === "-") {
      while (i < n && text[i] !== "\n") i++;
      continue;
    }
    if (c === "/" && d === "*") {
      const e = text.indexOf("*/", i + 2);
      i = e < 0 ? n : e + 2;
      continue;
    }
    if (c === "'" || c === '"') {
      i++;
      while (i < n) {
        if (text[i] === c) {
          if (text[i + 1] === c) i += 2;
          else break;
        } else i++;
      }
      i++;
      continue;
    }
    if (c === "$") {
      const m = /^\$[A-Za-z_]*\$/.exec(text.slice(i));
      if (m) {
        const e = text.indexOf(m[0], i + m[0].length);
        i = e < 0 ? n : e + m[0].length;
        continue;
      }
    }
    if (c === "(") depth++;
    if (c === ")") depth = Math.max(0, depth - 1);
    if (c === ";" && depth === 0) {
      // psql처럼 괄호 안의 ;는 문장 끝으로 보지 않아요.
      const s = text.slice(start, i + 1);
      if (s.replace(/--[^\n]*/g, "").trim() !== ";") out.push(s);
      start = i + 1;
    }
    i++;
  }
  const rest = text.slice(start);
  return { stmts: out.map(trimStmt).filter(Boolean), rest: rest.replace(/--[^\n]*/g, "").trim() ? rest.trim() : "" };
}
function trimStmt(s) {
  // 앞의 빈 줄과 주석 줄은 떼어요(psql도 빈 줄은 보내지 않아요).
  const lines = s.split("\n");
  while (lines.length && (lines[0].trim() === "" || /^\s*--/.test(lines[0]))) lines.shift();
  return lines.join("\n").replace(/^\s+/, "");
}

/** 줄이 시작할 때의 상태로 psql 이어지는 줄 표시를 골라요: -# 보통, (# 괄호 안, '# 따옴표 안 */
function contMarks(stmt) {
  const marks = [];
  let depth = 0;
  let q = null;
  for (let i = 0; i < stmt.length; i++) {
    const c = stmt[i];
    if (c === "\n") {
      marks.push(q === "'" ? "'" : q === '"' ? '"' : depth > 0 ? "(" : "-");
      continue;
    }
    if (q) {
      if (c === q) q = null;
      continue;
    }
    if (c === "-" && stmt[i + 1] === "-") {
      while (i + 1 < stmt.length && stmt[i + 1] !== "\n") i++;
      continue;
    }
    if (c === "'" || c === '"') q = c;
    else if (c === "(") depth++;
    else if (c === ")") depth = Math.max(0, depth - 1);
  }
  return marks;
}

/** psql이 보여 주는 명령 결과 이름(CREATE TABLE, INSERT 0 1 …) */
function tag(stmt, r) {
  const words = stmt
    .replace(/--[^\n]*/g, " ")
    .replace(/\/\*[\s\S]*?\*\//g, " ")
    .trim()
    .split(/\s+/)
    .map((w) => w.replace(/[;(].*$/, "").toUpperCase());
  const cmd = (r.command || words[0] || "").toUpperCase();
  const n = r.affectedRows ?? 0;
  if (cmd === "INSERT") return `INSERT 0 ${n}`;
  if (cmd === "UPDATE" || cmd === "DELETE" || cmd === "MERGE" || cmd === "FETCH" || cmd === "MOVE" || cmd === "COPY") return `${cmd} ${n}`;
  if (cmd === "SELECT") return `SELECT ${r.rowCount ?? r.rows.length}`;
  if (cmd === "CREATE" || cmd === "DROP" || cmd === "ALTER") {
    let k = 1;
    const skip = new Set(["OR", "REPLACE", "TEMP", "TEMPORARY", "UNIQUE", "UNLOGGED", "MATERIALIZED", "IF", "NOT", "EXISTS"]);
    while (k < words.length && skip.has(words[k])) k++;
    let obj = words[k] || "";
    if (obj === "USER") obj = "ROLE";
    const mat = words.slice(1, k).includes("MATERIALIZED") ? "MATERIALIZED " : "";
    // CREATE TABLE ... AS SELECT 는 SELECT n
    if (cmd === "CREATE" && obj === "TABLE" && / AS\s+(SELECT|WITH|VALUES|TABLE)\b/i.test(stmt)) return `SELECT ${n}`;
    return `${cmd} ${mat}${obj}`;
  }
  if (cmd === "TRUNCATE") return "TRUNCATE TABLE";
  if (cmd === "START") return "START TRANSACTION";
  return cmd;
}

/** 오류를 psql 모양으로: ERROR, LINE과 ^, DETAIL, HINT */
export function formatError(e, stmt) {
  const sev = e.severity || "ERROR";
  const lines = [`${sev}:  ${e.message}`];
  const pos = Number(e.position);
  if (pos > 0 && stmt) lines.push(...errorPosition(stmt, pos));
  if (e.detail) lines.push(...`DETAIL:  ${e.detail}`.split("\n"));
  if (e.hint) lines.push(...`HINT:  ${e.hint}`.split("\n"));
  return lines;
}

// libpq의 reportErrorPosition과 같은 방식(긴 줄은 60칸으로 자르고 ...)
function errorPosition(query, pos) {
  const DISPLAY = 60;
  const MINR = 10;
  const chars = [...query.replace(/\t/g, " ")];
  const loc = Math.min(pos - 1, chars.length);
  const scr = [0];
  let line = 1;
  let ibeg = 0;
  for (let i = 0; i < chars.length; i++) {
    const c = chars[i];
    scr.push(scr[i] + (c === "\n" || c === "\r" ? 0 : dw(c)));
    if ((c === "\n" || c === "\r") && i < loc) {
      line++;
      ibeg = i + 1;
    }
  }
  let iend = chars.length;
  for (let i = loc; i < chars.length; i++) {
    if (chars[i] === "\n" || chars[i] === "\r") {
      iend = i;
      break;
    }
  }
  let bt = false;
  let et = false;
  if (scr[iend] - scr[ibeg] > DISPLAY) {
    if (scr[ibeg] + DISPLAY >= scr[loc] + MINR) {
      while (scr[iend] - scr[ibeg] > DISPLAY) iend--;
      et = true;
    } else {
      while (scr[loc] + MINR < scr[iend]) {
        iend--;
        et = true;
      }
      while (scr[iend] - scr[ibeg] > DISPLAY) {
        ibeg++;
        bt = true;
      }
    }
  }
  const prefix = `LINE ${line}: ${bt ? "..." : ""}`;
  const text = chars.slice(ibeg, iend).join("");
  const off = dw(prefix) + scr[loc] - scr[ibeg];
  return [prefix + text + (et ? "..." : ""), " ".repeat(off) + "^"];
}

/**
 * SQL 엔진 하나. PGlite 생성자를 받아요(브라우저와 Node가 서로 다른 곳에서 불러요).
 * run(cell)은 새 데이터베이스에 setup, prelude, code를 차례로 넣고 code의 psql 화면만 돌려줘요.
 */
// 수업 컨테이너(postgres:18 공식 이미지)와 같은 시간대 이름이에요.
const TZ = "SET TIME ZONE 'Etc/UTC';";

export function makeSql(PGlite, opts = {}) {
  const parsers = rawParsers();
  const bases = new Map(); // setup 글자 → 그 상태의 데이터 폴더(tar)
  let db = null;

  async function fresh(setup) {
    if (db) {
      try {
        await db.close();
      } catch {
        /* 이미 닫힘 */
      }
      db = null;
    }
    const key = setup || "";
    if (!bases.has(key)) {
      const pg = await PGlite.create({ parsers, ...opts.pglite });
      await pg.exec("SET client_min_messages = warning;");
      if (setup) await pg.exec(setup);
      await pg.exec("RESET client_min_messages;");
      bases.set(key, await pg.dumpDataDir("none"));
      await pg.close();
    }
    db = await PGlite.create({ parsers, loadDataDir: bases.get(key), ...opts.pglite });
    await db.exec(TZ);
    return db;
  }

  /** 문장 하나를 실행하고 psql 화면 줄을 돌려줘요. tx: 트랜잭션 상태('' | '*' | '!') */
  async function one(pg, stmt, state) {
    const out = [];
    const notices = [];
    const onNotice = (m) => notices.push(...formatError(m, stmt));
    try {
      const res = await pg.exec(stmt, { parsers, onNotice, rowMode: "array" });
      out.push(...notices);
      for (const r of res) {
        const cmd = (r.command || "").toUpperCase();
        const hasRows = r.fields && r.fields.length > 0;
        if (hasRows || cmd === "SELECT") {
          out.push(...formatTable(r.fields || [], r.rows || []));
          if (cmd !== "SELECT" && cmd !== "SHOW" && cmd !== "EXPLAIN" && cmd !== "VALUES" && cmd !== "TABLE") out.push(tag(stmt, r));
        } else {
          out.push(tag(stmt, r));
        }
        if (cmd === "BEGIN" || cmd === "START") state.tx = "*";
        else if (cmd === "COMMIT" || cmd === "ROLLBACK" || cmd === "END" || cmd === "ABORT") state.tx = "";
      }
    } catch (e) {
      out.push(...notices, ...formatError(e, stmt));
      if (state.tx) state.tx = "!";
    }
    return out;
  }

  /** 줄들을 psql 프롬프트를 붙여 그대로 보여 줘요(아직 실행하지 않은 조각). */
  function echo(text, prompt, state) {
    const marks = contMarks(text);
    return text.split("\n").map((l, i) => `${prompt}${i === 0 ? "=" : marks[i - 1]}${state.tx}# ${l}`.trimEnd());
  }

  /** 수강생이 친 글자를 psql 화면처럼: 프롬프트와 문장, 결과. ^C 줄은 psql처럼 치던 문장을 버려요. */
  async function session(pg, code, prompt, state) {
    const lines = [];
    const segs = code.split(/^\^C[ \t]*$\n?/m);
    let rest = "";
    for (let k = 0; k < segs.length; k++) {
      const r = splitSql(segs[k]);
      for (const s of r.stmts) {
        lines.push(...echo(s, prompt, state));
        lines.push(...(await one(pg, s, state)));
      }
      rest = r.rest;
      if (k < segs.length - 1) {
        // 치던 문장을 ^C로 버린 자리
        const pend = rest ? echo(rest.replace(/\n$/, ""), prompt, state) : [];
        const m = rest ? contMarks(rest + "\n").pop() : "=";
        lines.push(...pend, `${prompt}${m}${state.tx}# ^C`);
        rest = "";
      }
    }
    if (rest) lines.push(...echo(rest, prompt, state));
    return { lines, rest };
  }

  return {
    /**
     * cell: { setup?: string, prelude?: string[], code: string, prompt?: string }
     * prelude는 앞 장에서 친 문장 묶음이에요. 묶음 하나가 psql 한 번이라, 끝나면 열린 트랜잭션을 버려요.
     */
    async run(cell) {
      const t0 = Date.now();
      const pg = await fresh(cell.setup);
      for (const block of cell.prelude || []) {
        const st = { tx: "" };
        for (const s of splitSql(block).stmts) {
          try {
            await pg.exec(s, { parsers });
            if (/^\s*(BEGIN|START)/i.test(s)) st.tx = "*";
            if (/^\s*(COMMIT|ROLLBACK|END)/i.test(s)) st.tx = "";
          } catch {
            /* 수업에서도 오류였던 문장이에요 */
          }
        }
        if (st.tx) await pg.exec("ROLLBACK;").catch(() => {});
        await pg.exec("RESET ALL;" + TZ).catch(() => {});
      }
      const state = { tx: "" };
      const { lines, rest } = await session(pg, cell.code, cell.prompt || "kant_shop", state);
      return { out: lines, rest, ms: Date.now() - t0 };
    },
    async close() {
      if (db) await db.close().catch(() => {});
      db = null;
    },
  };
}
