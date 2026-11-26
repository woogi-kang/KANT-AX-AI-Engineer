// 파이썬 실습 칸의 엔진 코드예요. 브라우저 워커(py-worker.mjs)와 자동 대조(scripts/practice-check.mjs)가 같이 써요.
// Pyodide(브라우저 안 파이썬)로 노트북 셀처럼 실행해요: 마지막 줄이 값이면 그 값을 보여 주고,
// 오류는 VS Code 노트북의 마지막 줄처럼 "이름: 설명" 한 줄로 보여 줘요.

export const MAX_LINES = 3000;

const RUNNER = `
import ast, sys, builtins, types, inspect

class _Out:
    def __init__(self, send, limit):
        self.send, self.limit, self.lines = send, limit, 0
    def write(self, s):
        self.lines += s.count("\\n")
        self.send(s)
        if self.lines > self.limit:
            raise KeyboardInterrupt("__too_long__")
        return len(s)
    def flush(self):
        pass

def _err_line(e):
    name = type(e).__name__
    if isinstance(e, SyntaxError):
        return f"{name}: {e.msg}"
    return f"{name}: {e}" if str(e) != "" else name

def _show(v):
    # VS Code 노트북(IPython)이 셀 마지막 값을 보여 주는 모양과 맞춰요.
    if isinstance(v, types.FunctionType):
        try:
            sig = str(inspect.signature(v))
        except Exception:
            sig = "(...)"
        return f"<function {v.__module__}.{v.__qualname__}{sig}>"
    t = type(v)
    if not isinstance(v, type) and t.__repr__ is object.__repr__:
        return f"<{t.__module__}.{t.__qualname__} at {hex(id(v))}>"
    return repr(v)

def _cell(src, ns, out):
    tree = ast.parse(src, "<cell>", "exec")
    last = None
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        last = ast.Expression(tree.body.pop().value)
    exec(compile(tree, "<cell>", "exec"), ns)
    if last is not None:
        v = eval(compile(last, "<cell>", "eval"), ns)
        if v is not None:
            out.write(_show(v) + "\\n")

def __practice_run(prelude, code, send, limit):
    ns = {"__name__": "__main__", "__builtins__": builtins}
    old = sys.stdout, sys.stderr
    sink = _Out(lambda s: None, 10**9)
    sys.stdout = sys.stderr = sink
    for p in prelude:
        try:
            _cell(p, ns, sink)
        except BaseException:
            pass
    out = _Out(send, limit)
    sys.stdout = sys.stderr = out
    status = "ok"
    try:
        _cell(code, ns, out)
    except KeyboardInterrupt as e:
        if str(e) == "__too_long__":
            status = "long"
        else:
            raise
    except BaseException as e:
        status = "err"
        send(_err_line(e) + "\\n")
    finally:
        sys.stdout, sys.stderr = old
    return status
`;

/** loadPyodide를 받아 엔진을 만들어요. */
export async function makePython(loadPyodide, opts = {}) {
  // 집합 순서가 실행할 때마다 바뀌지 않게 고정해요(수업 화면과 같다는 뜻은 아니에요).
  const py = await loadPyodide({ ...opts, env: { PYTHONHASHSEED: "0", ...(opts.env || {}) } });
  py.runPython(RUNNER);
  const fn = py.globals.get("__practice_run");
  return {
    py,
    async loadPackages(names) {
      if (names && names.length) await py.loadPackage(names, { messageCallback: () => {} });
    },
    /** cell: { prelude?: string[], code } → { out: string[], status } */
    async run(cell, onChunk) {
      const t0 = Date.now();
      let buf = "";
      const send = (s) => {
        buf += s;
        if (onChunk) onChunk(s);
      };
      const prelude = py.toPy(cell.prelude || []);
      let status;
      try {
        status = fn(prelude, cell.code, send, MAX_LINES);
      } finally {
        prelude.destroy();
      }
      const out = buf.replace(/\n$/, "").split("\n");
      return { out: buf === "" ? [] : out, status, ms: Date.now() - t0 };
    },
  };
}
